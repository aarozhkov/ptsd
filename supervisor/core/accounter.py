import yaml
import os
from random import randrange
from shared.models.account import Account
from shared.core.log import Log
from shared.core.yamlparser import YamlParser, ModelParser


log = Log('DEBUG')


class Accounter(ModelParser):
    def __init__(self):
        super(Accounter, self).__init__(model=Account)

    def get_random_account_for_brand(self, brand):
        accounts = self.pool.get(brand)
        if not accounts:
            return
        index = randrange(len(accounts))
        return accounts[index]


# data = parser.parse("accounts.yaml")
# accounter = Accounter(data)

accounter = Accounter()

if __name__=="__main__":
    accounter.parse_file("accounts.yaml")
    spec = accounter.get_element("RC-Commercial")
    log.debug(str(spec))

