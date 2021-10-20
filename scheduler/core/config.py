from typing import List, Optional, Dict
from pydantic import BaseSettings
from pydantic_yaml import YamlModel

from models.data import Account, Brand


class SchedulerSettings(BaseSettings):
    task_queue_maxlen: int
    push_interval: int
    accounter_address: Optional[str]
    superviser_address: str
    accounts: Optional[List[Account]]
    brands: Optional[List[Brand]]
    ptd_addresses: Optional[Dict[str, List]]
    ptr_addresses: Optional[List[str]]
    yaml_config: str
    max_test_in_progress: int


class YamlSchedulerConfig(YamlModel):
    brands: List[Brand]
    ptd_addresses: Dict[str, List]
    ptr_addresses: List[str]


config = SchedulerSettings()

if config.yaml_config:
    parsed_yaml = YamlSchedulerConfig.parse_file(config.yaml_config)
    config.ptd_addresses = parsed_yaml.ptd_addresses
    config.brands = parsed_yaml.brands
    config.ptr_addresses = parsed_yaml.ptr_addresses
