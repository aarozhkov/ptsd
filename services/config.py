# TODO this is not service. Should be transfered to different place
# TODO split PTR PTL configrations

from typing import Dict, List, Optional

from pydantic import BaseSettings
from starlette.config import Config

from models.data import Account, Brand

# Due to needness get data from config we cant relay only on ENV vars
# But this possability is available.


class SuperVisorConfig(BaseSettings):
    brands: List[Brand]
    ptr: Optional[List[str]]  # TODO for backward compitability phase 0
    # TODO for backward compatibility phase 0
    ptd: Optional[Dict[str, List[str]]]


class AccountsConfig(BaseSettings):
    accounts: List[Account]


config = Config(".env")
CONFIG_PATH = config("PTSD_CONFIG", cast=str, default="superviser.json")
ACCOUNT_CONF_PATH = config("ACCOUNT_CONFIG", cast=str, default="accounts.json")
SUPERVISOR_CONFIG = SuperVisorConfig.parse_file(CONFIG_PATH)
# ACCOUNT_CONFIG = AccountsConfig.parse_file(ACCOUNT_CONF_PATH)


# status service
STATUS_MAXTEST = config("STATUS_MAXTEST", cast=str, default="1000")
STATUS_MAX_RES_GROUP = config("STATUS_MAX_RES_GROUP", cast=str, default="3")
STATUS_REPORT_TIMEFRAME = config("STATUS_REPORT_TIMEFRAME", cast=str, default="60")
STATUS_DEF_GROUPING = config(
    "STATUS_DEF_GROUPING", cast=str, default="partition.unit.brand.location.test"
)
