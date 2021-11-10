from typing import Optional

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
