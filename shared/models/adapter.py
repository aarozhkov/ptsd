from typing import Optional, Set
from pydantic import BaseModel, constr

class TestRequest(BaseModel):
    version: str = '0.1'
    url: str = 'http://127.0.0.1:8114'
    ptd_address: str = 'http://127.0.0.1:4444'
    phone_or_email: str = '1234567890'
    extension: Optional[str]
    password: str
    test_suite: str = 'video'
    notify_on_complete: Optional[bool]
    test_id: int
