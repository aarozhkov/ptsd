from fastapi.applications import FastAPI

from scheduler.core.config import SchedulerSettings
from .queue import AbstractTaskQueue
from shared.models.brand import Brand
from shared.models.task import TestTask
from typing import List, Optional
from uuid import uuid4
import random
import asyncio
import logging


class SchedulerException(Exception):
    """Wrap all scheduler related exceptions"""


class Scheduler:
    def __init__(
        self,
        queue: AbstractTaskQueue,
        brands: List[Brand],
        push_interval: int = 1,
        logger: Optional[logging.Logger] = None,
    ):
        self.q = queue
        self.brands: List[Brand] = brands
        self.bucket = self.create_bucket(brands)
        self.push_interval = push_interval
        self.log = logger if logger else logging.getLogger(self.__class__.__name__)
        # To prevent run several pusher tasks outside Scheduler class
        self._runned_task = None

    def create_bucket(self, brands: List[Brand]) -> List[str]:
        """Generate list buket filled with brands in desired quontity."""
        result = []
        for brand in brands:
            for _ in range(brand.desired_rate):
                result.append(brand.name)
        return result

    def _get_brand_url(self, brand_name):
        for brand in self.brands:
            if brand.name == brand_name:
                return brand.entrypoint

    async def push_test_task(self):
        brand_to_schedule = self._get_randomly()
        await self.q.push(
            TestTask(
                id=uuid4(),
                brand=brand_to_schedule,
                brand_url=self._get_brand_url(brand_to_schedule),
                test_suit="video",  # FIXME from configuration
            )
        )

    def run(self):
        """Run pusher task if not yet runned"""
        if self._runned_task:
            raise SchedulerException("Scheduler pusher already runned")
        loop = asyncio.get_event_loop()
        self._runned_task = loop.create_task(self.pusher())
        self.log.debug("Scheduler runned %s", self._runned_task)

    def stop(self):
        if self._runned_task:
            self._runned_task.cancel()
        return

    def _get_randomly(self):
        num = random.random() * len(self.bucket)
        return self.bucket[int(num)]

    async def pusher(self):
        # FIXME: can it be runned without endless loop? Hard to test and control
        self.log.debug("asdasd")
        while True:
            try:
                await asyncio.sleep(self.push_interval)
                await self.push_test_task()
            except asyncio.CancelledError:
                self._runned_task = None
                break
                # log task canceletion


def init_scheduler(app: FastAPI, config: SchedulerSettings, queue: AbstractTaskQueue):
    scheduler = Scheduler(
        queue=queue, brands=config.brands, push_interval=config.push_interval
    )

    @app.on_event("startup")
    async def run_scheduler():
        scheduler.run()

    @app.on_event("shutdown")
    def stop_scheduler():
        scheduler.stop()
