# this is example service
import asyncio
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from prometheus_client import Gauge

ACTUAL_VALUE = Gauge("dummy_value", "DummyService parameters value", ["param_name"])


class DummyServiceException(Exception):
    """Named exception"""


class DummyService:
    def __init__(self, value: int = 0):
        self.value = value
        # TODO define params

    def set_value(self, value: int) -> bool:
        self.value = value
        ACTUAL_VALUE.labels("some_view").set(self.value)
        return True

    def get_value(self) -> int:
        return self.value

    def init(self, config: dict):
        try:
            self.set_value(config["value"])
        except KeyError as e:
            raise DummyServiceException("Provided config not contain value field", e)

    async def run(self):
        while True:
            await asyncio.sleep(2)
            _ = self.set_value(self.value + 1)

    def start(self):
        asyncio.create_task(self.run())


dummy_service = DummyService()


async def test(q: Optional[str] = "partition", skip: int = 0, limit: int = 100):

    if q and q not in ["brand", "partition", "unit", "location", "test"]:
        raise HTTPException(status_code=400, detail=f"Unknown group name: {q}")
    result = {"q": q, "skip": skip, "limit": limit}
    return result


router = APIRouter(prefix="/dummy", tags=["dummy"])


@router.get("/test")
async def get_test(data: dict = Depends(test)):
    return test


@router.get("/value")
async def get_dummy_value():
    return {"value": dummy_service.get_value()}


@router.post("/value")
def set_dummy_value(value: int):
    if dummy_service.set_value(value):
        return {"success": True, "value": dummy_service.get_value()}
    else:
        return {"success": False}
