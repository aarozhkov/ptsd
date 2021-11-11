from pydantic import BaseModel
from typing import Optional, Union
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
    test_id: UUID  # make it uuid
    test_suit: str
    brand: str
    location: str
    # partition: Union[str, None] = None
    # unit: Union[str, None] = None
    # allure_link: Union[str, None] = None
    # log_link: Union[str, None] = None
    partition: Optional[str] = None
    unit: Optional[str] = None
    allure_link: Optional[str] = None
    log_link: Optional[str] = None
    ptr_address: str  # check if we still need it? It is a part of logs at least
    date_time: datetime  # isoformat
    status: str
    # status: ResultEnum
    reason: Optional[str] = None
    duration: int
