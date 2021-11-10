import asyncio
from fastapi import FastAPI
from starlette_exporter import PrometheusMiddleware, handle_metrics
from scheduler.core.accounteer import LocalAccounteer


from .core.config import config
from .core.scheduler import Scheduler
from .core.queue import AsyncInMemoryQ
from .core.conveer import conveer_router, init_conveers


def init_services():
    if not config.accounteer:
        raise Exception("No config for LocalAccounteer service")
    if not config.scheduler or not config.conveer:
        raise Exception("No config for Scheduler and Conveer %s", config)
    task_queue = AsyncInMemoryQ(max_len=config.queue.task_queue_maxlen)
    accounteer = LocalAccounteer(accounts=config.accounteer.accounts)
    scheduler = Scheduler(queue=task_queue, **config.scheduler.dict())
    conveers = init_conveers(config.conveer, task_queue, accounteer)
    return scheduler, conveers


def init():
    app = FastAPI(title="scheduler")
    app.add_middleware(
        PrometheusMiddleware,
        app_name="scheduler",
        prefix="http",
        buckets=[0.1, 0.25, 0.5],
    )
    app.add_route("/metrics", handle_metrics)
    app.include_router(conveer_router)


@app.on_event("startup")
async def set_services():
    # FIXME: set separate functions
    scheduler, conveers = init_services()
    scheduler.run()
    for conveer in conveers:
        conveer.run()


@app.on_event("shutdown")
async def clean_services():
    for task in asyncio.Task.all_tasks():
        task.cancel()
