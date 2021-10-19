from .queue import AbstractTaskQueue
from models.data import Brand
from models.tests import TestTask
from typing import List
from uuid import uuid4
import random


class Scheduler:
    def __init__(self, queue: AbstractTaskQueue, brands: List[Brand]):
        self.q = queue
        self.bucket = self.create_bucket(brands)

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

    #     def run(self):
    #         create_task(self.pusher(), name="Scheduler-task-writer")

    def _get_randomly(self):
        num = random.random() * len(self.bucket)
        return self.bucket[int(num)]


#     async def pusher(self):
#         while True:
#             task = TestTask(
#                 id=uuid4(),
#                 brand=self.get_randomly(),
#                 rcw_version="21.3.30",  # FIXME from versionchecker
#                 test_suit="video",  # FIXME from configuration
#             )
#             await self.q.push(task)
