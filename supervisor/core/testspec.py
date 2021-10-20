from shared.models.testspec import TestSpec
from shared.core.yamlparser import ModelParser
from shared.core.log import Log

log = Log('DEBUG')


specificator = ModelParser(TestSpec)

if __name__=="__main__":
    specificator.parse_file("spec.yaml")
    spec = specificator.get_element("RC-Commercial")
    log.debug(str(spec))


