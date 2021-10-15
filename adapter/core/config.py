import yaml

class AdapterConfigParser():
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
