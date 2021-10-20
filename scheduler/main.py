import asyncio
from fastapi import FastAPI
from starlette_exporter import PrometheusMiddleware, handle_metrics

from scheduler.core.utils import fetch_brands

from .core.config import config


from .core.scheduler import Scheduler
from .core.queue import AsyncInMemoryQ
from .core.conveer import Conveer


app = FastAPI(title="scheduler")
app.add_middleware(
    PrometheusMiddleware, app_name="scheduler", prefix="http", buckets=[0.1, 0.25, 0.5]
)
app.add_route("/metrics", handle_metrics)


@app.on_event("startup")
async def set_services():
    # FIXME: set separate functions
    task_queue = AsyncInMemoryQ(max_len=config.task_queue_maxlen)
    if not config.brands:
        config.brands = fetch_brands(config.superviser_address)
    scheduler = Scheduler(
        queue=task_queue, brands=config.brands, periodicity=config.push_interval
    )
    scheduler.run()
    location = "ams"
    conveer = Conveer(
        task_queue=task_queue,
        ptd_address=config.ptd_addresses[location][0],
        location=location,
        max_test_in_progress=config.max_test_in_progress,
    )
    conveer.run()
    # for location, ptds in config.ptd_addresses.items():
    #     for ptd in ptds:
    #         conveer = Conveer(
    #             task_queue=task_queue,
    #             ptd_address=ptd,
    #             location=location,
    #             max_test_in_progress=config.max_test_in_progress,
    #         )
    #         conveer.run()


@app.on_event("shutdown")
async def clean_services():
    for task in asyncio.Task.all_tasks():
        task.cancel()
