from fastapi import FastAPI
from starlette_exporter import PrometheusMiddleware, handle_metrics
from scheduler.core.accounteer import LocalAccounteer


from .core.config import config
from .core.scheduler import init_scheduler
from .core.queue import AsyncInMemoryQ
from .core.conveer import init_conveers
import logging


def init_logging():
    # log_levels = {
    #     "info": logging.INFO,
    #     "debug": logging.DEBUG,
    #     "warning": logging.WARN
    # }
    # log_level = args.log_level or os.environ.get("LOG_LEVEL", "info")
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(module)s - %(message)s", level=logging.DEBUG
    )


def init_application():
    init_logging()
    if not config.accounteer:
        raise Exception("No config for LocalAccounteer service")
    if not config.scheduler or not config.conveer:
        raise Exception("No config for Scheduler and Conveer %s", config)
    app = FastAPI(title="scheduler_conveers")
    app.add_middleware(
        PrometheusMiddleware,
        app_name="scheduler",
        prefix="http",
        buckets=[0.1, 0.25, 0.5],
    )
    app.add_route("/metrics", handle_metrics)
    task_queue = AsyncInMemoryQ(max_len=config.queue.task_queue_maxlen)
    accounteer = LocalAccounteer(accounts=config.accounteer.accounts)
    init_scheduler(app=app, config=config.scheduler, queue=task_queue)
    init_conveers(
        app=app, config=config.conveer, task_queue=task_queue, accounteer=accounteer
    )
    return app


app = init_application()


if __name__ == "__main__":
    raise Exception("Straight run not implemented. Use uvicorn:...app for run")
