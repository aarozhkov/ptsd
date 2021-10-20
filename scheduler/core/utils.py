from scheduler.core.scheduler import SchedulerException
from models.data import Brand
from typing import List


def to_camel(underscored: str) -> str:
    """Cust snake case to CamelCase can be switched to pyhumps.camelize"""
    tokens = underscored.split("_")
    return tokens[0] + "".join([token.capitalize() for token in tokens[1:]])


def fetch_brands(supervisor_address: str) -> List[Brand]:
    """Implement async fetch here"""
    raise SchedulerException
