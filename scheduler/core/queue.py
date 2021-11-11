from typing import Protocol, runtime_checkable
from shared.models.task import TestTask
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


class AsyncInMemoryQ:
    def __init__(self, max_len=100):
        QUEUE_MAXLEN.set(max_len)
        self.queues_map = Queue(maxsize=max_len)

    async def push(self, task: TestTask):
        await self.queues_map.put(task)
        QUEUE_LEN.inc()

    async def get(self) -> TestTask:
        result = await self.queues_map.get()
        QUEUE_LEN.dec()
        return result
        # try:
        #     result = await self.queues_map.get()
        #     QUEUE_LEN.dec()
        #     return result
        # except CancelledError:
        #     self.queues_map.task_done()
