import logging

from fastapi import FastAPI
from starlette_exporter import PrometheusMiddleware, handle_metrics

from services.dummy_service import dummy_service
from services.dummy_service import router as dummy_router
from services import config
from services.status import StatusService, router as status_router
from services.router import router as test_router

# from services.scheduler import GenericQ, Scheduler

# from services.config import superviser_config

logger = logging.getLogger()
logging.basicConfig(
    format="%(asctime)s %(levelname)s %(module)s - %(message)s", level=logging.INFO
)

app = FastAPI()

app.add_middleware(
    PrometheusMiddleware, app_name="superviser", prefix="http", buckets=[0.1, 0.25, 0.5]
)
app.add_route("/metrics", handle_metrics)


@app.on_event("startup")
async def app_startup():
    logger.info("Startup")
    # TODO config object initialisation
    # TODO VersionChecker checker initialisation
    # TODO Scheduler initialisation
    # TODO Accounter initialisation
    # TODO Status initialisation

    # execute async run function for all workers
    # asyncio.create_task(version_checker.run())
    # asyncio.create_task(version_checker.run())
    # asyncio.create_task(scheduler.run())
    # asyncio.create_task(accounter.run())
    # asyncio.create_task(accounter.run())
    status = StatusService(
        maxtests=config.STATUS_MAXTEST,
        max_results_per_category=5,
        report_expiration=config.STATUS_REPORT_TIMEFRAME,
    )
    app.dependency_overrides[StatusService] = lambda: status
    dummy_service.init({"value": 255})
    dummy_service.start()


# FIXME For now i can suggest to approach:
# 1. Include route initialisation in service modulesself.
#       HEre i cant found how to clearly initiate Services
# 2. route intialisation on superuser
#       Here all initialisation can be done on superviser level. - More obvious


app.include_router(dummy_router)
app.include_router(status_router)
app.include_router(test_router)


@app.get("/status")
async def root():
    # TODO return supervisor git revision aka version
    return {"status": "ok"}


# app.include_router(router)
