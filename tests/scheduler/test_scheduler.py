from models.tests import TestTask
from scheduler.core.scheduler import Scheduler
from models.data import Brand
from unittest.mock import Mock, AsyncMock, patch
import pytest
from collections import Counter
import asyncio


@pytest.fixture
def test_brands():
    brands = [
        {
            "name": "ATOS",
            "url": "https://video.cloudwork.bt.com/",
            "test_suite": "video",
            "units_count": 2,
        },
        {
            "name": "RC-Commercial",
            "url": "https://v.ringcentral.com",
            "test_suite": "video",
            "units_count": 6,
        },
    ]
    return [Brand.parse_obj(brand) for brand in brands]


def test_scheduler_init(test_brands):
    q = Mock()
    scheduler = Scheduler(queue=q, brands=test_brands)
    assert scheduler.q == q


def test_scheduler_backet_init(test_brands):
    q = Mock()
    scheduler = Scheduler(queue=q, brands=test_brands)
    generated_probability = Counter(scheduler.bucket)
    assert generated_probability["ATOS"] == 2
    assert generated_probability["RC-Commercial"] == 6


@pytest.mark.asyncio
async def test_scheduler_push_task(test_brands):
    mocked_task_queue = AsyncMock()
    scheduler = Scheduler(queue=mocked_task_queue, brands=[test_brands[0]])
    await scheduler.push_test_task()
    mocked_task_queue.push.assert_called_once()
    test_task = mocked_task_queue.push.call_args.args[0]  #
    assert isinstance(test_task, TestTask)
    assert test_task.brand == test_brands[0].name


@pytest.mark.asyncio
async def test_scheduler_background_task(test_brands):
    """There should be code to check async background function it self"""
    """ Function is a endless loop, yet not check how to check cancelation
        try: catch block

        try:
            task
        except asyncio.CancelledError:
            release scheduler
    """
    # FIXME: TEst smels. Need to check before sleep, need to check canceleation
    mocked_task_queue = AsyncMock()
    push_period = 2
    scheduler = Scheduler(
        queue=mocked_task_queue, brands=[test_brands[0]], periodicity=push_period
    )
    test_background_task = asyncio.create_task(scheduler.pusher())
    assert test_background_task is not None

    # Wait more then setted push_period
    await asyncio.sleep(push_period + 1)
    test_background_task.cancel()
    assert scheduler._runned_task is None
    # Expect pusher
    mocked_task_queue.push.assert_called_once()


# @pytest.mark.skip
@pytest.mark.asyncio
def test_scheduler_run_async_background_job(test_brands):
    mocked_task_queue = Mock()
    mocked_return_value = "mocked_task"
    with patch(
        "scheduler.core.scheduler.asyncio.create_task",
        Mock(return_value=mocked_return_value),
    ) as mocked_asyncio:
        scheduler = Scheduler(queue=mocked_task_queue, brands=[test_brands[0]])
        scheduler.run()
        mocked_asyncio.assert_called_once()
        assert scheduler._runned_task == mocked_return_value
