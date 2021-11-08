from fastapi import FastAPI, BackgroundTasks, Response
from models.tests import PtrOutcome
from scheduler.core.conveer import PTRResult, PTRTask
import random
import requests
import logging
from uuid import UUID
import asyncio
from starlette.config import Config
from starlette import datastructures


logger = logging.getLogger(__name__)

app = FastAPI(title="Dummy_PTR")
config = Config(".env")
NOTIFICATION_CALLBACK = config("PTR_CALLBACK", datastructures.URLPath)


GLOBAL_TASKS = 0
MAX_TASKS = 2

TEST_ID = 12333


def random_partition_unit():
    partitions = ["us-01", "us-02", "us-03"]
    units = ["iad41", "sjc01", "iad01"]
    fixture_partition = random.choice(partitions)
    fixture_unit = f"{fixture_partition}-{random.choice(units)}"
    return fixture_partition, fixture_unit


def random_result():
    return "PASSED" if random.random() > 0.2 else "FAILED"


def send_notification(notification_url: str, ptr_result: PTRResult):
    try:
        result = requests.post(notification_url, json=ptr_result.json())
        result.raise_for_status()
        return
    except Exception as e:
        logger.exception("Notification failed, ", e)
        return


async def test_result_generator(test_id: int, task: PTRTask):
    status = (random_result(),)
    part, unit = random_partition_unit()
    call_id = f"{UUID()}!{unit}@{part}"
    outcome = PtrOutcome(
        name=task.test_suite, status=status, call_id=call_id, reason=""
    )
    result = PTRResult(
        ptr_test_id=test_id, ptr_index=task.ptr_index, outcomes=[outcome]
    )
    await asyncio.sleep(60 + (30 + random.random()))
    send_notification(NOTIFICATION_CALLBACK, result)
    return


@app.post("/test")
def dummy_test(task: PTRTask, response: Response, background_tasks: BackgroundTasks):
    if GLOBAL_TASKS > MAX_TASKS:
        response.status_code = 529
        return {"message": "I am busy. Fuck off!"}
    global TEST_ID
    TEST_ID += 1
    background_tasks.add_task(test_result_generator, TEST_ID, task)
    response.status_code = 200
    return
