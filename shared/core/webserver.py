import uvicorn
from fastapi import FastAPI
from shared.core.exporter import prometheus_router
from starlette_exporter import PrometheusMiddleware


class SomeFastApiApp(FastAPI):
    def __init__(self, app_name="some_app"):
        super().__init__()
        self.add_middleware(PrometheusMiddleware, app_name=app_name)
        self.include_router(prometheus_router)


if __name__=='__main__':
    app = SomeFastApiApp()
    uvicorn.run(app, host="0.0.0.0", port=8000)

