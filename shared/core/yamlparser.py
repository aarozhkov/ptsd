import yaml
from shared.core.log import Log
log = Log('DEBUG')

class YamlParser():
    def _parse_yaml(self, config):
        try:
            with open(config, 'r') as conf:
                try:
                    data = yaml.safe_load(conf)
                except yaml.YAMLError as e:
                    log.error('Parsing configuration failed', stack=e)
        except FileNotFoundError:
            log.error(f"File {config} is not found")
            return {}

        return data

    def parse(self, path):
        data = self._parse_yaml(path)
        return data

class ModelParser(YamlParser):
    def __init__(self, model):
        self.pool = {}
        self.model = model
#       self._parse_model(config)


    def parse_file(self, path):
        data = self.parse(path)
        self.parse_model(data)


    def parse_model(self, data):
        for key, value in data.items():
            instances = []
            for element in value:
                try:
                    instance = self.model(**element)
                    instances.append(instance)
                except Exception as e:
                    log.error(f'Found invalid element {element} in configuration', stack=e)

            self.pool.update({key: instances})

    def get_element(self, key):
        value = self.pool.get(key)
        return value


