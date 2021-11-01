from fastapi.routing import APIRouter
from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Optional
import logging
import asyncio
import random

from scheduler.core.config import ConveerSettings
from services.versionchecker import VersionChecker
from shared.models.account import Account
from httpx import AsyncClient
from enum import Enum

from shared.models.task import TestTask
from models.tests import TestResult
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
    password: str
    test_suite: str
    target_partition_unit: Optional[str]
    notify_on_complete: bool
    ptr_index: Optional[int]  # Backward compatibility
    # there is no such thing in original but how i can achive that?
    notify_url: Optional[str]

    class config:
        alias_generator = to_camel


class ResultEnum(Enum):  # From java test stdout on PTR side
    passed = "PASSED"
    failed = "FAILED"


class PtrOutcome(BaseModel):
    """Standard callback notification Payload in PTR"""

    test_id: str
    status: ResultEnum
    call_id: Optional[str]
    reason: Optional[str]
    duration: int

    class config:
        alias_generator = to_camel


class PTRResult(BaseModel):
    ptr_test_id: str
    ptr_index: int
    outcomes: List[PtrOutcome]

    class config:
        alias_generator = to_camel


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
        version_checker: Optional[VersionChecker],
        logger: Optional[logging.Logger] = None,
    ):
        self.q = task_queue
        self.accounteer = accounteer
        self.ptd_addresses = ptd_addresses
        self.ptr_addresses = ptr_addresses
        self.location = location
        self.name = f"conveer_{location}"
        self.max_test_in_progress = max_test_in_progress
        self.tests: Dict[str, List] = dict(
            zip(self.ptd_addresses, [[]] * len(self.ptd_addresses))
        )
        self.version_checker = version_checker if version_checker else VersionChecker()
        self.log = logger if logger else logging.getLogger(self.__class__.__name__)
        self._runned_task = None

    def _get_ptr(self):
        num = random.random() * len(self.ptr_addresses)
        return self.ptr_addresses[int(num)]

    async def _get_task(self) -> TestTask:
        """get task from queue"""
        task = await self.q.get()
        self.log.debug("Got task: %s" % task)
        return task

    async def _gen_ptr_request(
        self, ptr, ptd, task: TestTask, account: Account
    ) -> PTRTask:
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
            notify_url="127.0.0.1:8080",
            ptr_index=ptr,
        )

    async def _push_to_ptr(
        self, ptr: str, ptd: str, account: Account, task: PTRTask
    ) -> bool:
        """Push task to provided ptr"""
        attempts = 3
        async with AsyncClient() as client:
            while attempts > 0:
                r = await client.post(f"{ptr}/test", json=task.json())
                if r.status_code == 200:
                    self.log.debug(
                        "Send task for %s to %s, used account: %s", ptd, ptr, account
                    )
                    return True
                if r.status_code == 529:
                    attempts += 1
        return False

    async def get_notification(self, test_result: TestResult):
        """get result notification from ptr"""
        self.log.debug("Got notification for: %s", test_result)

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
        self.tests[ptd].append(
            {"task_id": task.id, "reserved_account": account}
        )  # Allocate test slot to prevent async collision
        self.log.debug("Task: %s in progress for %s", task.id, ptd)
        # FIXME: must use first available. How to implement this?
        ptr = self._get_ptr()
        ptr_task = await self._gen_ptr_request(ptr, ptd, task, account)
        task_pushed = await self._push_to_ptr(ptr, ptd, account, ptr_task)
        if not task_pushed:
            # FIXME send notification aboutfailed task
            self.tests[ptd].remove({"task_id": task.id, "reserved_account": account})
            await self.accounteer.release_account(account)
            self.log.debug("Delete failed task from in-progress list for %s", ptd)
        return

    async def _fetcher(self):
        """Infinite loop on fetching tasks from queue"""
        while True:
            try:
                await asyncio.sleep(2)
                for ptd in self.tests:
                    _ = asyncio.create_task(self._add_task(ptd), name=f"{ptd} task add")
            except asyncio.CancelledError:
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


# FIXME somehow change GLOBAL state usage
GLOBAL_CONVEER_STATE = {}


def init_conveers(
    config: ConveerSettings, task_queue: AbstractTaskQueue, accounteer: Accounteer
):
    for location in config.ptd_addresses:
        GLOBAL_CONVEER_STATE[location] = Conveer(
            task_queue=task_queue,
            accounteer=accounteer,
            ptd_addresses=config.ptd_addresses[location],
            ptr_addresses=config.ptr_addresses,
            location=location,
            max_test_in_progress=config.max_test_in_progress,
            version_checker=VersionChecker(),
        )

conveer_router = APIRouter(tags="conveer notification")

@conveer_router.post("/test-completed")
def test_notification(test_result: PTRResult):


