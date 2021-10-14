from typing import Optional, Set
from pydantic import BaseModel, constr

#targetPartitionUnitRegexp = constr(regex="/(\S+)@(\S+): (\d)/g")

class TestRequest(BaseModel):
    version: str
    url: str
    ptdAddress: str
    phoneOrEmail: str
    extension: Optional[str]
    password: str
    testSuite: str
    convName: str
    jsonxml: Optional[str]
    targetPartitionUnit: Optional[str]
    #targetPartitionUnit: Optional[Set[targetPartitionUnitRegexp]]
    notifyOnComplete: Optional[bool]
    ptrIndex: Optional[int]
