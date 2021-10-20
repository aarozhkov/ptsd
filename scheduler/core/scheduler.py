from .queue import AbstractTaskQueue
from models.data import Brand
from models.tests import TestTask
from typing import List
from uuid import uuid4
import random
import asyncio


class SchedulerException(Exception):
    """Wrap all scheduler related exceptions"""


class Scheduler:
    def __init__(
        self, queue: AbstractTaskQueue, brands: List[Brand], periodicity: int = 1
    ):
        self.q = queue
        self.bucket = self.create_bucket(brands)
        self.period = periodicity
        # To prevent run several pusher tasks outside Scheduler class
        self._runned_task = None

    def create_bucket(self, brands: List[Brand]) -> List[str]:
        """Generate list buket filled with brands in desired quontity."""
        result = []
        for brand in brands:
            for _ in range(brand.units_count):
                result.append(brand.name)
        return result

    async def push_test_task(self):
        await self.q.push(
            TestTask(
                id=uuid4(),
                brand=self._get_randomly(),
                rcw_version="21.3.30",  # FIXME from versionchecker
                test_suit="video",  # FIXME from configuration
            )
        )

    def run(self):
        """Run pusher task if not yet runned"""
        if self._runned_task:
            raise SchedulerException("Scheduler pusher already runned")
        self._runned_task = asyncio.create_task(
            self.pusher(), name="scheduler-task-pusher"
        )

    def _get_randomly(self):
        num = random.random() * len(self.bucket)
        return self.bucket[int(num)]

    async def pusher(self):
        # FIXME: can it be runned without endless loop? Hard to test and control
        while True:
            try:
                await asyncio.sleep(self.period)
                await self.push_test_task()
            except asyncio.CancelledError:
                self._runned_task = None
                break
                # log task canceletion
