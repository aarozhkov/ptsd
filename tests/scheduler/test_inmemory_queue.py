import asyncio
from models.tests import TestTask
from scheduler.core.queue import AbstractTaskQueue, AsyncInMemoryQ
from prometheus_client import REGISTRY
import pytest
from uuid import uuid4


@pytest.fixture
def test_task():
    return TestTask(
        id=uuid4(),
        brand="Atos",
        brand_url="https://video.unifyoffice.com",
        test_suit="video",
    )


def test_inmemory_queue_is_TaskQueue():
    assert issubclass(AsyncInMemoryQ, AbstractTaskQueue)


def test_inmemory_queue_initialization():
    q = AsyncInMemoryQ(max_len=2)
    maxlen_metric = REGISTRY.get_sample_value("test_task_queue_max_size")
    assert isinstance(q.queues_map, asyncio.Queue)
    assert q.queues_map.maxsize == 2
    assert maxlen_metric == 2


@pytest.mark.asyncio
async def test_inmemory_queue_put_get(test_task):
    q = AsyncInMemoryQ()
    await q.push(test_task)
    assert q.queues_map.qsize() == 1
    metric = REGISTRY.get_sample_value("test_task_queue_size")
    assert metric == 1
    queued_task = await q.get()
    assert queued_task == test_task
    final_metric = REGISTRY.get_sample_value("test_task_queue_size")
    assert final_metric == 0
