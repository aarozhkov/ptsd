from pydantic import BaseModel
from typing import List, Optional



class Account(BaseModel):
    phone_or_email: str
    extension: List[int]
    password: str

