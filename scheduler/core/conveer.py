from datetime import datetime
from fastapi.applications import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter
from pydantic import BaseModel, HttpUrl, SecretStr
from typing import List, Dict, Optional, Tuple
import logging
import asyncio
import random
from pytz import UTC

from scheduler.core.config import ConveerSettings
from scheduler.core.version_checker import VersionChecker
from shared.models.account import Account
from httpx import AsyncClient
from enum import Enum

from shared.models.task import TestTask, TestResult
from scheduler.core.accounteer import Accounteer
from .queue import AbstractTaskQueue
from .utils import to_camel

""" This class is adapter between new architecture and old one with PTR """
""" Class will repeat Conveyor service functionality in PTL """
""" Grub task from Task Queue, grab additional information and send to PTR"""


class PTRTask(BaseModel):
    version: str  # RCV release version for right uptc usage
    url: str  # RCV web app endpoint url: v.ringcentral.com
    ptd_address: str
    phone_or_email: str
    extension: Optional[int]
    password: SecretStr
    test_suite: str
    target_partition_unit: Optional[str]
    notify_on_complete: bool
    ptr_index: Optional[int]  # Backward compatibility
    # there is no such thing in original but how i can achive that?
    # notify_url: Optional[str]

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        json_encoders = {
            SecretStr: lambda v: v.get_secret_value() if v else None,
        }


class ResultEnum(Enum):  # From java test stdout on PTR side
    passed = "PASSED"
    failed = "FAILED"


class PtrOutcome(BaseModel):
    """Standard callback notification Payload in PTR"""

    name: str
    status: ResultEnum
    call_id: Optional[str]
    reason: Optional[str]
    # duration: int FIXME: conveer WILL calculate this!!!
    # FIXME: conveer must fixate startTime before send test task!!!

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class PTRResult(BaseModel):
    ptr_test_id: str  # this is generated on PTR
    ptr_index: int  # Returns back from PTR task request
    outcomes: List[PtrOutcome]

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class ConveerException(Exception):
    """Specific conveer cases"""


class Conveer:
    """Set conveer to supervise all ptd in single location"""

    def __init__(
        self,
        task_queue: AbstractTaskQueue,
        accounteer: Accounteer,
        ptd_addresses: List[HttpUrl],
        ptr_addresses: List[HttpUrl],
        location: str,
        max_test_in_progress: int,
        status_notify: str = "http://localhost:8090/api/v1/test-report",
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
        partition, unit = self._extract_core(ptr_result.outcomes)
        allure_link = f"{ptr}/test/{ptr_test_id}/allure/"
        log_link = f"{ptr}/test/{ptr_test_id}/log/"
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
            status=ptr_result.outcomes[0].status.value,
            reason=ptr_result.outcomes[0].reason,
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
            extension=account.extension,
            password=account.password,
            test_suite=task.test_suit,
            notify_on_complete=True,
            # notify_url="127.0.0.1:8080",
            ptr_index=self.conveer_id,
        )

    async def _push_to_status(self, test_result: TestResult) -> bool:
        """Push task to provided ptr"""
        attempts = 3
        async with AsyncClient() as client:
            while attempts > 0:
                # FIXME because we use PASSWORD as secure
                r = await client.post(
                    self.status_notify,
                    headers={"Content-Type": "application/json"},
                    data=test_result.json(),
                )
                if r.status_code == 200:
                    self.log.debug("Send test report to status service %s", r.content)
                    return True
                if r.status_code == 529:
                    attempts += 1
                if r.status_code == 422:
                    self.log.debug(r.content)
                    return False
        return False

    async def _push_to_ptr(self, ptr: str, ptd: str, task: PTRTask) -> bool:
        """Push task to provided ptr"""
        attempts = 3
        async with AsyncClient() as client:
            while attempts > 0:
                # FIXME because we use PASSWORD as secure
                r = await client.post(
                    f"{ptr}/test",
                    headers={"Content-Type": "application/json"},
                    data=task.json(),
                )
                if r.status_code == 200:
                    self.log.debug(
                        "Send task for %s to %s, used account: %s", ptd, ptr, r.content
                    )
                    return r.json().get("ptrTestId", None)
                if r.status_code == 529:
                    attempts += 1
                if r.status_code == 422:
                    self.log.debug(r.content)
        return False

    async def get_notification(self, test_result: TestResult):
        """get result notification from ptr"""
        self.log.debug("Got notification for: %s", test_result)

    async def get_notification_legacy(self, ptr_result: PTRResult):
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
        self.log.debug("Got to wrong place %s, %s", self.tasks, ptr_result)
        return False
        # TODO implement send to Status
        # TODO implement test duration calculation

    async def _add_task(self, ptd):
        """Check tasks in progress for each ptd
        Send task if test in progress not reach maximum
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
