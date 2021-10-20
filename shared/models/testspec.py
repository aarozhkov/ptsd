from pydantic import BaseModel



class TestSpec(BaseModel):
    version : str
    entrypoint: str
    testSuite: str
    desiredRate: int

