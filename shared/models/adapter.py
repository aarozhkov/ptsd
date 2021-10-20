from typing import Optional, Set
from pydantic import BaseModel, constr

#targetPartitionUnitRegexp = constr(regex="/(\S+)@(\S+): (\d)/g")

class TestRequest(BaseModel):
    version: str = '0.1'
    url: str = 'http://127.0.0.1:8114'
    ptdAddress: str = 'http://127.0.0.1:4444'
    phoneOrEmail: str = '1234567890'
    extension: Optional[str]
    password: str
    testSuite: str = 'video'
    convName: str = 'sjc_1'
    # jsonxml: Optional[str] # Depricated. We use only JSON.
    targetPartitionUnit: Optional[str] = 'us-01@sjc01:10'
    #targetPartitionUnit: Optional[Set[targetPartitionUnitRegexp]]
    notifyOnComplete: Optional[bool]
    ptrIndex: Optional[int]
