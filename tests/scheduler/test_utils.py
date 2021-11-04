from shared.models.account import Account
from scheduler.core.utils import parse_accounts, to_camel


def test_to_camel():
    entry = "test_sname_case"
    assert "testSnameCase" == to_camel(entry)


def test_account_parser_config():
    config = {
        "RC-Commercial": [
            {
                "phoneOrEmail": "14706495518",
                "extension": "101-103",
                "password": "Test!123",
            },
            {
                "phoneOrEmail": "19167504977",
                "extension": "105",
                "password": "Test!123",
                "partition": "us-01",
            },
        ],
        "Phoenix": [
            {
                "phoneOrEmail": "mm5+3019604@ag20210224124338-2456.dins.ru",
                "password": "Test!123",
            }
        ],
        "Verizon": [
            {
                "phoneOrEmail": "+14706503610",
                "extension": "101",
                "password": "Test!123",
            }
        ],
    }
    accounts = parse_accounts(config)
    assert any(isinstance(account, Account) for account in accounts)
    assert len(accounts) == 6
    assert (
        len([account for account in accounts if account.brand == "RC-Commercial"]) == 4
    )
