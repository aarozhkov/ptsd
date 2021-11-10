from pydantic import BaseModel, SecretStr
from typing import Optional


class Account(BaseModel):
    brand: str
    phone_or_email: str
    extension: Optional[int]
    password: SecretStr
