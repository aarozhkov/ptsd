from pydantic import BaseModel
from enum import Enum
from typing import Optional
from .account import Account
from .brand import Brand


class TestTask(BaseModel):
    id: int  # Uniq id for scheduled task
    brand: Brand
    # scheduled task is async. We not sure exact time of execution. Account must be asquired on execution time.
    host_account: Optional[Account]


class ResultEnum(Enum):  # From java test stdout on PTR side
    passed = "PASSED"
    failed = "FAILED"


class PtrOutcome(BaseModel):
    """Standard callback notification Payload in PTR"""

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
