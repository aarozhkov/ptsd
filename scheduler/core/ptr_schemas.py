""" Ptr Legacy API payload Schemas """
from typing import Optional, List, Any
from pydantic import BaseModel, SecretStr
from enum import Enum
from .utils import to_camel


class CamelCaseBase(BaseModel):
    # NOTE:
    # This is data serialization schema. Used for api calls
    # to save backward compitability and general rules:
    # This schemas must be covverted from pythonic snake_case ti JSON camelcase
    # Passwords must be serialised in api calls but shadowed in LOG messages
    # log messages shoud use .dict() call.

    class Config:

        alias_generator = to_camel
        allow_population_by_field_name = True
        json_encoders = {
            SecretStr: lambda v: v.get_secret_value() if v else None,
        }


class PTRTask(CamelCaseBase):
    version: str  # RCV release version for right uptc usage
    url: str  # RCV web app endpoint url: v.ringcentral.com
    ptd_address: str
    phone_or_email: str
    extension: Optional[str]
    password: SecretStr
    test_suite: str
    conv_name: str
    target_partition_unit: Optional[str]
    notify_on_complete: bool
    ptr_index: Optional[int]  # Backward compatibility
    # there is no such thing in original but how i can achive that?
    # notify_url: Optional[str]


class ResultEnum(Enum):  # From java test stdout on PTR side
    passed = "PASSED"
    failed = "FAILED"


class PtrOutcome(CamelCaseBase):
    """Standard callback notification Payload in PTR"""

    name: str
    status: ResultEnum
    call_id: Optional[str]
    reason: Optional[str]


class PTRResult(CamelCaseBase):
    ptr_test_id: int  # this is generated on PTR
    ptr_index: int  # Returns back from PTR task request
    outcomes: List[PtrOutcome]


class AdapterResult(BaseModel):
    test_id: Any[UUID, str]
    call_id: Optional[str] = None
    allure_link: Optional[str] = None
    log_link: Optional[str] = None
    status: str
    reason: Optional[str] = None
