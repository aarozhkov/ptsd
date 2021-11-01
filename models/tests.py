from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel

# from models.data import Brand

# structs from js part


class ResultEnum(Enum):  # From java test stdout on PTR side
    passed = "PASSED"
    failed = "FAILED"


# Generated from java run stdout on PTR side
# Strings like:
#   Test name: twoUsersAreAbleToSeeEachOther_p2pOff, Status: FAILED, Call id: null, Reason: org.openqa.selenium.TimeoutException: Unable to click on join audio by computer buttonself.
#   Test name: twoUsersAreAbleToSeeEachOther_p2pOff, Status: PASSED, Call id: 81b1ca2b-b9a4-49dd-972b-b4f38db4ceb3!us-03-iad41@us-03, Reason: null
class PtrOutcome(BaseModel):
    test_id: str
    status: ResultEnum
    call_id: Optional[str]
    reason: Optional[str]
    duration: int


class TestNotification(BaseModel):
    ptrTestId: int
    ptrIndex: int
    outcomes: List[PtrOutcome]


class ResultOutcome(BaseModel):
    test_id: str
    status: ResultEnum
    reason: Optional[str]
    duration: int


class TestResult(BaseModel):
    test: str  # Name of java test-NG test
    brand: str  # do i need to put Brand object here? Witch information it will use?
    location: str  # not sure if it needed, location can be defined by source queue
    partition: str
    unit: str
    allure_link: str
    log_link: str  # Can we switch it to ELK usage?
    ptr_address: str  # check if we still need it? It is a part of logs at least
    date_time: datetime  # isoformat
    outcome: ResultOutcome


# New structs:


class TestTask(BaseModel):
    id: int
    brand: str
    brand_url: str
    test_suit: str


class ReportResponse(BaseModel):
    success: bool
    groupBy: str
    rcv: dict


class GenericResponse(BaseModel):
    success: bool
    result: Optional[dict]
    failure: Optional[str]
