from asyncio.exceptions import CancelledError
from .queue import AbstractTaskQueue
from models.data import Brand
from models.tests import TestTask
from typing import List
from uuid import uuid4
import random
import asyncio


class Scheduler:
    def __init__(self, queue: AbstractTaskQueue, brands: List[Brand]):
        self.q = queue
        self.bucket = self.create_bucket(brands)
        self.runned = False

    def create_bucket(self, brands: List[Brand]) -> List[str]:
        """will return list of tuples (brand, location)"""
        result = []
        for brand in brands:
            for _ in range(brand.units_count):
                result.append(brand.name)
        return result

    async def add_task(self):
        await self.q.push(
            TestTask(
                id=uuid4(),
                brand=self._get_randomly(),
                rcw_version="21.3.30",  # FIXME from versionchecker
                test_suit="video",  # FIXME from configuration
            )
        )

    def run(self):
        asyncio.create_task(self.pusher(), name="scheduler-task-pusher")

    def _get_randomly(self):
        num = random.random() * len(self.bucket)
        return self.bucket[int(num)]

    async def pusher(self):
        while True:
            try:
                await self.add_task()
            except asyncio.CancelledError:
                # runned flag should be here
                # log task canceletion 
