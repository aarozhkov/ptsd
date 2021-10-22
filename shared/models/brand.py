from pydantic import BaseModel


class Brand(BaseModel):
    name: str
    version: str
    entrypoint: str
    test_suite: str
    desired_rate: int
