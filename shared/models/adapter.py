from typing import Optional, Union
from uuid import UUID

from pydantic import BaseModel


class TestRequest(BaseModel):
    version: str
    url: str
    ptd_address: str
    phone_or_email: str
    extension: Optional[str]
    password: str
    test_suite: str
    notify_on_complete: Optional[bool]
    test_id: int
    conv_id: str


class AdapterRequest(BaseModel):
    version: str
    url: str
    ptd_address: str
    phone_or_email: str
    extension: Optional[str] = None
    password: str
    test_suite: str
    test_id: int
    conv_id: str


class AdapterResult(BaseModel):
    test_id: Union[UUID, str]
    call_id: Optional[str] = None
    allure_link: Optional[str] = None
    log_link: Optional[str] = None
    status: str
    reason: Optional[str] = None
    ptd_address: str
