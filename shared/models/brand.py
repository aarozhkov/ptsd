from pydantic import BaseModel


class Brand(BaseModel):
    name: str
    # Version can be changed while task scheduled
    # version: Optional[str]
    entrypoint: str
    test_suite: str
    desired_rate: int
