from pydantic import BaseModel
from typing import List
import logging
import asyncio

from models.tests import TestResult
from .queue import AbstractTaskQueue
from .utils import to_camel

logging.basicConfig(level=logging.INFO)

""" This class is adapter between new architecture and old one with PTR """
""" Class will repeat Conveyor service functionality in PTL """
""" Grub task from Task Queue, grab additional information and send to PTR"""


class PTRTask(BaseModel):
    version: str
    url: str
    ptd_address: str
    phone_or_email: str
    extension: int
    password: str
    test_suite: str
    conv_name: str
    target_partition_unit: str
    notify_on_complete: bool
    ptr_index: int

    class config:
        alias_generator = to_camel


class ConveerException(Exception):
    """Specific conveer cases"""


class Conveer:
    def __init__(
        self,
        task_queue: AbstractTaskQueue,
        ptd_address: str,
        location: str,
        max_test_in_progress: int,
    ):
        self.q = task_queue
        self.ptd_address = ptd_address  # address
        self.location = location
        self.name = f"{location}_{ptd_address[-7:]}"
        self.max_test_in_progress = max_test_in_progress
        self.test: List = []
        self.log = logging.getLogger(self.__class__.__name__)
        self._runned_task = None

    async def get_task(self):
        """get task from queue"""
        task = await self.q.get()
        self.log.info("Got task: %s" % task)

    async def push_to_ptr(self):
        """push to random ptr"""

    async def get_account(self):
        """get account from accounter"""

    def run(self):
        """run task fetcher on background"""
        """Run pusher task if not yet runned"""
        if self._runned_task:
            raise ConveerException("Conveer fetcher already runned")
        self._runned_task = asyncio.create_task(
            self.fetcher(), name=f"{self.name}-task-fetcher"
        )

    async def get_notification(self, test_result: TestResult):
        """get result notification from ptr"""

    async def fetcher(self):
        """Infinite loop on fetching tasks from queue"""
        while True:
            try:
                await asyncio.sleep(2)
                await self.get_task()
            except asyncio.CancelledError:
                self._runned_task = None
                break
