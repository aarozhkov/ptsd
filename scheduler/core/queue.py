from typing import Protocol, runtime_checkable
from models.tests import TestTask
from prometheus_client import Gauge
from asyncio import Queue


QUEUE_LEN = Gauge(
    "test_task_queue_size",
    "Scheduled test task count in queue ",
)

QUEUE_MAXLEN = Gauge(
    "test_task_queue_max_size",
    "Maximum size test tasks queue",
)


@runtime_checkable
class AbstractTaskQueue(Protocol):
    async def push(self, task: TestTask):
        """Abstract method to push TestTask in queue"""

    async def get(self) -> TestTask:
        """Abstract method to get task From queue"""

    async def done(self, TestTask):
        """Abstract method to notify Task is processed and can be removed"""


class AsyncInMemoryQ:
    def __init__(self, max_len=100):
        QUEUE_MAXLEN.set(max_len)
        self.queues_map = self._create_queues(max_len)

    @classmethod
    def _create_queues(cls, max_len):
        return Queue(maxsize=max_len)

    async def push(self, task: TestTask):
        await self.queues_map.put(task)
        QUEUE_LEN.inc()

    async def get(self) -> str:
        QUEUE_LEN.dec()
        return await self.queues_map.get()

    async def done(self, task: TestTask):
        return
