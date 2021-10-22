from pydantic import BaseModel
from typing import Optional


class Account(BaseModel):
    phone_or_email: str
    extension: Optional[int]
    password: str
