import yaml
import os
from random import randrange
from shared.models.account import Account


class Accounter():
    def __init__(self, data):
        self.pool = {}
        self._parse_accounts(data)


    def _parse_accounts(self, data):
        for key, value in data.items():
            accounts = []
            for element in value:
                try:
                    account = Account(**element)
                    accounts.append(account)
                except Exception as e:
                    print(f"Found ivalid account {element} in account list " + repr(e))

            self.pool.update({key: accounts})


    def get_random_account_for_brand(self, brand):
        accounts = self.pool.get(brand)
        index = randrange(len(accounts))
        return accounts[index]


class AccountsParser():
    def _parse_yaml(self, config):
        with open(config, 'r') as conf:
            try:
                data = yaml.safe_load(conf)
            except yaml.YAMLError as e:
                print("Parsing configuration failed with: " + repr(e))

        return data

    def parse(self, path):
        data = self._parse_yaml(path)
        print(data)
        return data


if __name__=="__main__":
    parser = AccountsParser()
    data = parser.parse("accounts.yaml")
    accounter = Accounter(data)
    account = accounter.get_random_account_for_brand("RC-Commercial")
    print(account)


