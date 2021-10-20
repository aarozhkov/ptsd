from fastapi import APIRouter, HTTPException, Depends
from starlette.requests import Request
from starlette.responses import Response
from supervisor.core.supervisor import supervisor



supervisor_router = APIRouter()


@supervisor_router.get("/account")
async def get_account(brand: str) -> Response:
    account = supervisor.accounter.get_element(brand)
    if not account:
        raise HTTPException(status_code=404, detail=f"No accounts were found for brand {brand}")
    return account


@supervisor_router.get("/spec")
async def get_specs(brand: str) -> Response:
    spec = supervisor.specificator.get_element(brand)
    if not spec:
        raise HTTPException(status_code=404, detail=f"No accounts were found for brand {brand}")
    return spec

