from typing import List, Optional

from pydantic import BaseModel
from pydantic.fields import Field

# Minimum for testNG:
# "hub" - selenoid hub
# "url", RCW url
# account info:
# "phoneOrEmail"
# "extension"
# "password",
# "pstnPhoneOrEmail"
# "pstnExtension"
# "pstnPassword",
# "dialInNumber"
# "targetPartitionUnit" - specific unit to test


class Account(BaseModel):
    phone_or_email: str
    extension: Optional[str]
    password: str
    partition: Optional[str]
    # In case we can start to generate accounts in pool
    due_date: Optional[str]
    # is_busy:  In new implementation it can be checked by pool location:
    #           pool: available_accounts -
    #           pool: ocupated_accounts


class Brand(BaseModel):
    name: str
    url: str
    # locations: list  # By new requerements we should not be aware of brand unit locations.
    test_suite: str
    units_count: int


class Launcher(BaseModel):
    ptd_list: list
    brands: List[Brand]  # TODO discover struct
    accounts: list  # TODO initAccounts(this.brands);
    conveyors: list


class Account_Group(BaseModel):
    group_name: str
    account_list: List[Account]


class Conveyor(BaseModel):
    name: str  # location_ptdIndex
    brands: list
    accounts: list
    location: str
    ptd_address: str
    status_page: str  # TODO this is a link to status_page object
