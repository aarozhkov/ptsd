import yaml
import pathlib
import os
import subprocess
from shared.core.log import Log

from filelock import Timeout, FileLock

log = Log('DEBUG')


class AdapterConfigParser():
    def _parse_yaml(self, config):
        with open(config, 'r') as conf:
            try:
                data = yaml.safe_load(conf)
            except yaml.YAMLError as e:
                log.error("Parsing configuration failed with: " + repr(e))

        return data

    def parse(self, path):
        data = self._parse_yaml(path)
        log.debug(data)
        return data


class Adapter():
    def buildJars(self):
        return True

    def runJars(self, XMLLocation, workDirectory):
        # TODO need to be in config file or something like that
        log.debug(
            f"java -javaagent:/app/result/builds/aspectjweaver.jar -jar /app/result/builds/UPTC.jar {XMLLocation} ----- {workDirectory}")
        result = subprocess.run([
            'java',
            '-javaagent:/app/result/builds/aspectjweaver.jar',
            '-jar',
            '/app/result/builds/UPTC.jar',
            XMLLocation
        ], stdout=subprocess.PIPE)

        with open(workDirectory + "/stdout.log", "w+") as f:
            f.write(result.stdout.decode('utf-8'))
            f.close()
        return True

    def saveTestNGXML(self, tests_directory, XML):
        # TODO add exceptions
        xmlLocation = tests_directory + "/testng.xml"
        with open(xmlLocation, "w+") as f:
            f.write(XML)
            f.close()
        return xmlLocation

    def callBackFunction(self):
        return True

    def createDirectory(self, path, testId):
        fullpath = path + "/" + str(testId)
        if (pathlib.Path(fullpath).mkdir(parents=True, exist_ok=True) is None):
            return fullpath
        else:
            # TODO Add exception
            return False

    def selenoidPush(self, XML):
        return True


    def getNextTestId(self, path):
        file_path = path + "/test.increment"
        lock_path = path + "/test.increment.lock"

        lock = FileLock(lock_path, timeout=1)

        with lock:
            last_id = 0

            if (os.path.exists(file_path)):
                with open(file_path, "r+") as f:
                    last_id = f.read()
                    if last_id.isdigit() == True:
                        last_id = int(last_id)
                    else:
                        last_id = 0
                    f.close()
            else:
                last_id = 0

            if (last_id > 0):
                next_id = last_id + 1
            else:
                next_id = 1

            with open(file_path, "w") as f:
                f.write(str(next_id))
                f.close()

        return next_id


    def startPipeline(self, XML):
        # TODO move to s3?
        
        base_tests_directory = "/app/result/tests"
        testId = self.getNextTestId(base_tests_directory)
        current_test_directory = self.createDirectory(base_tests_directory, testId)
        xmlLocation = self.saveTestNGXML(current_test_directory, XML)
        # log.debug(xmlLocation)
        log.debug(xmlLocation)
        self.runJars(xmlLocation, current_test_directory)

        return True

    def initTestNg(self, data, config):
        targetPartitionUnit = data.targetPartitionUnit  # ? data.targetPartitionUnit : ""
        extension = data.extension  # ? data.extension : ""
        methods = ""

        try:
            classes = config["testSuites"][data.testSuite]
            # TODO Add catch exceptions

            for method in classes["methods"]:
                method = method["name"]
                methods += f"<include name=\"{method}\" />\n"

            include = f"""<class name="{classes["name"]}">
                        <methods>
                            {methods}
                        </methods>
                    </class>"""

            xml = f"""<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE suite SYSTEM "http://testng.org/testng-1.0.dtd">
        <suite name="RCV">
            <parameter name="hub" value="{data.ptdAddress}" />
            <parameter name="url" value="{data.url}" />
            <test name="MainFlow">
                <parameter name="phoneOrEmail" value="{data.phoneOrEmail}" />
                <parameter name="extension" value="{extension}" />

                <parameter name="password" value="{data.password}" />
                <parameter name="pstnPhoneOrEmail" value="{data.phoneOrEmail}" />
                <parameter name="pstnExtension" value="{extension}" />
                <parameter name="pstnPassword" value="{data.password}" />

                <parameter name="dialInNumber" value="16504191505" />
                <parameter name="targetPartition" value="{targetPartitionUnit}" />

                <classes>
                    {include}
                </classes>
            </test>
        </suite>"""
            return xml
        except:
            return False


if __name__ == "__main__":
    parser = AdapterConfigParser()
    config = parser.parse("adapter/adapter.yaml")
