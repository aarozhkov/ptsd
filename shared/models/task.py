from datetime import datetime
from typing import Optional, Union
from uuid import UUID

from pydantic import BaseModel


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
    # FIXME this is not Generic test result.
    #       need to implement "generic" result storage.
    test_id: UUID  # make it uuid
    test_suit: str
    brand: str
    location: str  # location of test executin
    partition: Optional[str] = None
    unit: Optional[str] = None
    allure_link: Optional[str] = None
    log_link: Optional[str] = None
    date_time: datetime  # isoformat
    status: str
    # status: ResultEnum
    reason: Optional[str] = None
    duration: int
