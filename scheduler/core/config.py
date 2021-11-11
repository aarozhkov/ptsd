from typing import List, Optional, Dict
from pydantic import BaseSettings, BaseModel, HttpUrl
from pydantic_yaml import YamlModel

from shared.models.account import Account
from shared.models.brand import Brand
from scheduler.core.utils import parse_accounts


class QueueSettings(BaseSettings):
    task_queue_maxlen: int = 10


class SchedulerSettings(BaseSettings):
    """Will grub ENV vars except for brands"""

    # superviser_address: str  # This is for Scheduler with auto rebalancing implementation
    brands: List[Brand]
    push_interval: int = 1


class ConveerSettings(BaseSettings):
    max_test_in_progress: int = 1
    status_notify: str = "http://localhost:8101/api/v1/test-report"
    ptd_addresses: Dict[str, List[str]]
    ptr_addresses: List[str]


class AccounteerSettings(BaseModel):
    accounts: List[Account]


class YamlConfig(YamlModel):
    brands: Optional[List[Brand]]
    ptd_addresses: Dict[str, List[str]]
    ptr_addresses: List[str]


class YamlAccountsConfig(YamlModel):
    # FIXME need to add config validation
    accounts: Dict[str, List]


class FlagsSettings(BaseSettings):
    """Component behavior flags"""

    # TODO: factory for scheduler implementation
    # TODO: factory for task queue implementation
    # TODO: switch flags for Conveer
    # scheduler: Scheduler
    # accounter: Accounteer
    # coveer: Conveer
    yaml_config: Optional[str]
    account_config: Optional[str]


class ComponentSettings(BaseModel):
    queue: QueueSettings = QueueSettings()
    scheduler: Optional[SchedulerSettings] = None
    conveer: Optional[ConveerSettings] = None
    accounteer: Optional[AccounteerSettings] = None


flags = FlagsSettings()
config = ComponentSettings()

if flags.yaml_config:
    parsed_yaml = YamlConfig.parse_file(flags.yaml_config)
    config.scheduler = SchedulerSettings(brands=parsed_yaml.brands)
    config.conveer = ConveerSettings(
        ptd_addresses=parsed_yaml.ptd_addresses, ptr_addresses=parsed_yaml.ptr_addresses
    )

if flags.account_config:
    parsed_accounts = YamlAccountsConfig.parse_file(flags.account_config)
    config.accounteer = AccounteerSettings(
        accounts=parse_accounts(parsed_accounts.dict()["accounts"])
    )
