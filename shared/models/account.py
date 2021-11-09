from pydantic import BaseModel, SecretStr
from typing import Optional


class Account(BaseModel):
    brand: str
    phone_or_email: str
    extension: Optional[int]
    password: SecretStr

    class Config:
        json_encoders = {
            SecretStr: lambda v: v.get_secret_value() if v else None,
        }
