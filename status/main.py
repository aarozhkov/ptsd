import uvicorn
from fastapi import FastAPI
from .storages.sql_store import db_init
from .api.status_router import router
from starlette_exporter import PrometheusMiddleware, handle_metrics


app = FastAPI(title="Status")
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", handle_metrics)
app.include_router(router)
db_init(app)


if __name__ == "__main__":
    uvicorn.run("status.main:app", host="0.0.0.0", port=8000)
