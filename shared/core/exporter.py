from fastapi import APIRouter
from starlette_exporter import handle_metrics
from starlette.requests import Request
from starlette.responses import Response

prometheus_router = APIRouter()

@prometheus_router.get("/metrics")
async def get_metrics(request: Request) -> Response:
    response = handle_metrics(request)
    return response

