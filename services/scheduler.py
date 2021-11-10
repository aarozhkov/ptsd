# Service implements test scheduler entity
# TODO: impelemnt simple scheduler on top
from asyncio import Queue, create_task

from models.tests import TestTask
from uuid import uuid4
import random
from prometheus_client import Counter

QUEUE_PUSH = Counter("ptl_scheduler_send_tasks", "Task sended by scheduler in Queue")


class GenericQ:
    def __init__(self, max_len=100):
        self.queues_map = self._create_queues(max_len)

    @classmethod
    def _create_queues(cls, max_len):
        return Queue(maxsize=max_len)

    async def push(self, task: TestTask):
        await self.queues_map.put(task)
        QUEUE_PUSH.inc()

    async def get(self) -> str:
        return await self.queues_map.get()


class Scheduler:
    def __init__(self, queue, brands):
        self.q = queue
        self.bucket = self.create_bucket(brands)

    def create_bucket(self, brands: dict):
        """will return list of tuples (brand, location)"""
        result = []
        for brand in brands:
            for _ in range(brands[brand]["unitsCount"]):
                result.append(brand)
        return result

    def run(self):
        create_task(self.pusher(), name="Scheduler-task-writer")

    def get_randomly(self):
        num = random.random() * len(self.bucket)
        return self.bucket[int(num)]

    async def pusher(self):
        while True:
            task = TestTask(
                id=uuid4(),
                brand=self.get_randomly(),
                rcw_version="21.3.30",  # FIXME from versionchecker
                test_suit="video",  # FIXME from configuration
            )
            await self.q.push(task)
