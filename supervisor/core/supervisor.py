from supervisor.core.accounter import Accounter
from shared.core.yamlparser import ModelParser
from shared.models.testspec import TestSpec



class Supervisor():
    def __init__(self):
        self.specificator = ModelParser(TestSpec)
        self.accounter = Accounter()

    def get_configs(self):
        self.specificator.parse_file("spec.yaml")
        self.accounter.parse_file("accounts.yaml")

supervisor = Supervisor()
supervisor.get_configs()



