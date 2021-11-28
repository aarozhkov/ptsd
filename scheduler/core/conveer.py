from datetime import datetime
from fastapi.applications import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter
from typing import List, Dict, Optional, Tuple
import logging
import asyncio
import random
from pytz import UTC
from prometheus_client import Counter

from scheduler.core.config import ConveerSettings
from scheduler.core.version_checker import VersionChecker
from shared.models.account import Account
from httpx import AsyncClient, HTTPStatusError

from shared.models.task import TestTask, TestResult
from scheduler.core.accounteer import Accounteer
from .ptr_schemas import AdapterResult, PTRTask, PTRResult, PtrOutcome, ResultEnum
from .queue import AbstractTaskQueue

""" This class is adapter between new architecture and old one with PTR """
""" Class will repeat Conveyor service functionality in PTL """
""" Grub task from Task Queue, grab additional information and send to PTR"""

# TODO:
# 1. Metrics for all failed tasks by PTSD fault
# 2. Metrics task in porgress?

TASK_FAILURES = Counter(
    "conveer_task_failed",
    "This metric count all task fails by internal conveer issues",
    ["conveer_id", "task_id", "executor", "reason"],
)


class ConveerException(Exception):
    """Specific conveer cases"""


class Conveer:
    """Set conveer to supervise all ptd in single location"""

    def __init__(
        self,
        task_queue: AbstractTaskQueue,
        accounteer: Accounteer,
        ptd_addresses: List[str],
        ptr_addresses: List[str],
        location: str,
        max_test_in_progress: int,
        status_notify: str,
        version_checker: Optional[VersionChecker] = None,
        logger: Optional[logging.Logger] = None,
    ):
        self.q = task_queue
        self.accounteer = accounteer
        self.ptd_addresses = ptd_addresses
        self.ptr_addresses = ptr_addresses
        self.location = location
        self.status_notify = status_notify
        # FIXME: For backward compitability with PTR
        #        and conveer identation on notifications will use uniq Conveer id
        #        it will be INT to feet ptrIndex type restrictions
        self.conveer_id = hash(location) % 10 ** 4
        self.name = f"conveer_{location}"
        self.max_test_in_progress = max_test_in_progress
        self.tests: Dict[str, Dict] = dict(
            zip(self.ptd_addresses, [{}] * len(self.ptd_addresses))
        )
        self.version_checker = version_checker if version_checker else VersionChecker()
        self.log = (
            logger if logger else logging.getLogger(f"Conveer: {self.conveer_id}")
        )
        self._runned_task = None

    def _get_ptr(self):
        num = random.random() * len(self.ptr_addresses)
        return self.ptr_addresses[int(num)]

    @classmethod
    def _extract_core(cls, outcomes: List[PtrOutcome]) -> Tuple:
        """Extract partition and unit from meeting id"""
        # Legacy Outcomes cames as list but it is always just one result
        # call_id: ae112473-4eaf-4e24-8474-f654560f858f!us-03-sjc01@us-03
        if not outcomes:
            return None, None

        call_id = outcomes[0].call_id
        if not call_id:
            return None, None
        partition, unit = call_id.split("!")[1].split("@")
        return partition, unit

    async def gen_task_result(
        self,
        ptr_result: PTRResult,
        start_time: datetime,
        task: TestTask,
        reserved_account: Account,
        ptr: str,
        ptr_test_id: str,
    ) -> TestResult:
        duration = (datetime.utcnow() - start_time).seconds
        if ptr_result.outcomes:
            status = ptr_result.outcomes[0].status.value
            reason = ptr_result.outcomes[0].reason
            allure_link = f"{ptr}/test/{ptr_test_id}/allure/"
            log_link = f"{ptr}/test/{ptr_test_id}/log/"
        else:
            status, reason = ResultEnum.failed.value, None
            allure_link, log_link = None, None
        partition, unit = self._extract_core(ptr_result.outcomes)
        await self.accounteer.release_account(reserved_account)
        return TestResult(
            test_id=task.id,
            test_suit=task.test_suit,
            brand=task.brand,
            location=self.location,
            partition=partition,
            unit=unit,
            allure_link=allure_link,
            log_link=log_link,
            ptr_address=ptr,
            date_time=start_time.replace(tzinfo=UTC),
            status=status,
            reason=reason,
            duration=duration,
        )

    async def _get_task(self) -> TestTask:
        """get task from queue"""
        task = await self.q.get()
        self.log.debug("Got task: %s" % task)
        return task

    async def _gen_ptr_request(self, ptd, task: TestTask, account: Account) -> PTRTask:
        # FIXME try catch if version will not work?
        version = await self.version_checker.get_version(task.brand_url)
        return PTRTask(
            version=version,
            url=task.brand_url,
            ptd_address=ptd,
            phone_or_email=account.phone_or_email,
            exTEnsion=account.extension,
            password=account.password,
            test_suite=task.test_suit,
            conv_name=str(task.id),
            notify_on_complete=True,
            ptr_index=self.conveer_id,
        )

    async def _push_to_status(self, test_result: TestResult) -> bool:
        """Push task to provided ptr"""
        attempts = 3
        self.log.debug(
            self.status_notify, test_result.json(by_alias=True, exclude_unset=True)
        )
        async with AsyncClient() as client:
            while attempts >= 0:
                try:
                    # FIXME because we use PASSWORD as secure
                    r = await client.post(
                        self.status_notify,
                        headers={"Content-Type": "application/json"},
                        content=test_result.json(by_alias=True, exclude_unset=True),
                    )
                    r.raise_for_status
                    self.log.debug("Send test report to status service %s", r.content)
                    return True
                except HTTPStatusError as e:
                    self.log.exception("Failed to deliver report", e)
                    return False
        return False

    async def _push_to_ptr(self, ptr: str, ptd: str, task: PTRTask) -> bool:
        """Push task to provided ptr. Will retry on 529 from PTR."""
        # FIXME: 529 should not be presented if max test capacity for ptr and conveer will be synced
        sended = False
        async with AsyncClient() as client:
            while not sended:
                try:
                    # FIXME because of serialisation.
                    # Have to use json. Probably we can add params to dict serialisation.
                    r = await client.post(
                        f"{ptr}/test",
                        headers={"Content-Type": "application/json"},
                        content=task.json(by_alias=True, exclude_unset=True),
                    )
                    r.raise_for_status()
                    self.log.debug(
                        "Send task for %s to %s, responce: %s", ptd, ptr, r.content
                    )
                    return r.json().get("ptrTestId", None)
                except HTTPStatusError as exc:
                    if exc.response.status_code == 529:
                        await asyncio.sleep(5)
                    else:
                        self.log.exception("Got issues on PTR api call: %s", exc)
                        return False
        return False

    async def get_task_callback(self, test_result: AdapterResult) -> bool:
        """get result notification from Adapter"""
        for ptd_queue in self.tests.values():
            if test_result not in ptd_queue.keys():
                return False

            self.log.debug("Got notification for Adapter: %s", test_result)
            return True
        return False

    async def get_notification_legacy(self, ptr_result: PTRResult) -> bool:
        """get result notification from ptr"""
        if ptr_result.ptr_index != self.conveer_id:
            return False
        for ptd_test_queue in self.tests:
            for task_id, value in self.tests[ptd_test_queue].items():
                if value["ptr_test_id"] == ptr_result.ptr_test_id:
                    test_result = await self.gen_task_result(ptr_result, **value)
                    notified = await self._push_to_status(test_result)
                    self.tests[ptd_test_queue].pop(task_id)
                    self.log.debug(
                        "Test result for: %s, sended successfully: %s",
                        test_result,
                        notified,
                    )
                    return True
        self.log.debug("Got to wrong place %s, %s", self.tests, ptr_result)
        return False

    async def _add_task(self, ptd):
        """Check tasks in progress for each ptd
        Send task if tests in progress count not reach maximum
        """
        if len(self.tests[ptd]) >= self.max_test_in_progress:
            return
        task = await self._get_task()
        account = await self.accounteer.book_account(task.brand)
        if not account:
            # FIXME send notification about failed task
            self.log.error("Cant book account for task: %s. Task will be lost", task.id)
            return
        ptr = self._get_ptr()
        self.tests[ptd][task.id] = {
            "task": task,
            "reserved_account": account,
            "ptr_test_id": None,
            "start_time": datetime.utcnow(),
            "ptr": ptr,
        }  # Allocate test slot to prevent async collision
        self.log.debug("Task: %s in progress for %s", task.id, ptd)
        # FIXME: must use first available. How to implement this?
        ptr_task = await self._gen_ptr_request(ptd, task, account)
        ptr_test_id = await self._push_to_ptr(ptr, ptd, ptr_task)
        if not ptr_test_id:
            # FIXME send notification aboutfailed task
            self.tests[ptd].pop(task.id)
            await self.accounteer.release_account(account)
            self.log.debug("Delete failed task from in-progress list for %s", ptd)
            return
        self.tests[ptd][task.id]["ptr_test_id"] = ptr_test_id
        return

    async def _fetcher(self):
        """Infinite loop on fetching tasks from queue"""
        while True:
            try:
                await asyncio.sleep(2)
                for ptd in self.tests:
                    _ = asyncio.create_task(self._add_task(ptd), name=f"{ptd} task add")
            except asyncio.CancelledError:
                self.log.debug("Task handling was stopped.")
                self._runned_task = None
                break

    def run(self):
        """run task fetcher on background"""
        """Run pusher task if not yet runned"""
        if self._runned_task:
            raise ConveerException("Conveer fetcher already runned")
        self._runned_task = asyncio.create_task(
            self._fetcher(), name=f"{self.name}-task-fetcher"
        )
        self.log.info("Coveer hashed id: %s started", self.conveer_id)

    def stop(self):
        if self._runned_task:
            self._runned_task.cancel()
        return


# FIXME somehow change GLOBAL state usage
GLOBAL_CONVEER_STATE: List[Conveer] = []


conveer_router = APIRouter(tags=["conveer", "ptr"])


@conveer_router.post("/test-completed")
async def legacy_test_notification(test_result: PTRResult):
    global GLOBAL_CONVEER_STATE
    result = False
    for conveer in GLOBAL_CONVEER_STATE:
        if await conveer.get_notification_legacy(test_result):
            result = True
            return {"success": True}
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"No test requester found for this test: {test_result.ptr_test_id}",
        )


@conveer_router.post("/api/v1/task_callback")
async def legacy_test_notification(test_result: PTRResult):
    global GLOBAL_CONVEER_STATE
    result = False
    for conveer in GLOBAL_CONVEER_STATE:
        if await conveer.get_notification_legacy(test_result):
            result = True
            return {"success": True}
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"No test requester found for this test: {test_result.ptr_test_id}",
        )


# Callback for adapter.
# @conveer_router.post("/api/v1/callback/{id}")
# async def test_callback(id: int)
# TODO: implement calback function for different conveers?


def init_conveers(
    app: FastAPI,
    config: ConveerSettings,
    task_queue: AbstractTaskQueue,
    accounteer: Accounteer,
):
    """Initialize all conveers and regester in FastAPI"""
    global GLOBAL_CONVEER_STATE
    for location in config.ptd_addresses:
        GLOBAL_CONVEER_STATE.append(
            Conveer(
                task_queue=task_queue,
                accounteer=accounteer,
                ptd_addresses=config.ptd_addresses[location],
                ptr_addresses=config.ptr_addresses,
                location=location,
                max_test_in_progress=config.max_test_in_progress,
                version_checker=VersionChecker(),
                status_notify=config.status_notify,
            )
        )
    app.include_router(conveer_router)

    @app.on_event("startup")
    def conveers_start() -> None:
        for conveer in GLOBAL_CONVEER_STATE:
            conveer.run()

    # TODO: on event stop?
    @app.on_event("shutdown")
    def conveers_stop():
        for conveer in GLOBAL_CONVEER_STATE:
            conveer.stop()
