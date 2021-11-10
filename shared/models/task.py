from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime
from uuid import UUID


class TestTask(BaseModel):
    id: UUID
    brand: str
    brand_url: str
    test_suit: str


# class ResultEnum(str, Enum):  # From java test stdout on PTR side
#     passed = "PASSED"
#     failed = "FAILED"


class TestResult(BaseModel):
    # TODO can we just extend TestTask?
    test_id: int  # make it uuid
    test_suit: str
    brand: str
    location: str
    partition: Optional[str]
    unit: Optional[str]
    allure_link: Optional[HttpUrl]
    log_link: Optional[HttpUrl]
    ptr_address: str  # check if we still need it? It is a part of logs at least
    date_time: datetime  # isoformat
    status: str
    # status: ResultEnum
    reason: Optional[str]
    duration: int
