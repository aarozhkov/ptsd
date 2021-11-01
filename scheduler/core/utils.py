from shared.models.account import Account
from typing import Iterable, List


def to_camel(underscored: str) -> str:
    """Cust snake case to CamelCase can be switched to pyhumps.camelize"""
    tokens = underscored.split("_")
    return tokens[0] + "".join([token.capitalize() for token in tokens[1:]])


def _gen_extension_range(extension: str) -> Iterable:
    start_stop = extension.split("-")
    if len(start_stop) == 1:
        return [int(start_stop[0])]
    return range(int(start_stop[0]), int(start_stop[1]) + 1)


def _inbrand_accounts(brand_accounts: List, brand: str) -> List:
    result = []
    for account in brand_accounts:
        if "@" in account["phoneOrEmail"] or not account["extension"]:
            result.append(
                {
                    "phone_or_email": account["phoneOrEmail"],
                    "password": account["password"],
                    "brand": brand,
                }
            )
            continue
        for ext in _gen_extension_range(account["extension"]):
            result.append(
                {
                    "phone_or_email": account["phoneOrEmail"],
                    "password": account["password"],
                    "extension": ext,
                    "brand": brand,
                }
            )

    return result


def parse_accounts(account_config: dict) -> List[Account]:
    result = []
    for brand, value in account_config.items():
        branded_accounts = _inbrand_accounts(value, brand)
        result.extend([Account.parse_obj(account) for account in branded_accounts])
    return result
