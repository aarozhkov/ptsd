import pathlib
import subprocess
import os.path

from shared.core.yamlparser import YamlParser
from shared.core.log import Log
from adapter.core.filestorage import FileStorage

log = Log("DEBUG")

class Adapter:
    def buildJars(self):
        return True

    def readinessProbe():
        return True

    def getAllureReport(testId):
        return True

    def getTestLog(testId):
        return True

    def generateAllureReport(self, config, testId, workDirectory):
        result = subprocess.run(
            ["allure", "generate", f"{workDirectory}/target/allure-results", "-o", f"{workDirectory}/allure"],
            stdout=subprocess.PIPE,
            cwd=workDirectory,
            timeout=config["testTimeout"],
        )
        with open(workDirectory + "/stdout.log", "a+") as f:
            f.write(result.stdout.decode("utf-8"))
            f.close()

        try:
            allureReportIndex = pathlib.Path(workDirectory + "/allure/index.html")
            allureReportIndex.resolve(strict=True)
        except FileNotFoundError:
            log.debug("FileNotFoundError: allure problem")
            return ""
        else:
            log.debug("Allure OK. Try Upload to s3")
            fs = FileStorage(config)
            reportUrl = fs.upload_directory(workDirectory, testId)
            return reportUrl

    def runJars(self, XMLLocation, config, workDirectory):
        buildsDirectory = config["dirs"]["buildsDir"]
        # TODO need to be in config file or something like that
        log.debug(
            f"java -javaagent:{buildsDirectory}/aspectjweaver.jar -jar {buildsDirectory}/UPTC.jar {XMLLocation} ----- {workDirectory}"
        )
        result = subprocess.run(
            [
                "java",
                f"-javaagent:{buildsDirectory}/aspectjweaver.jar",
                "-jar",
                f"{buildsDirectory}/UPTC.jar",
                XMLLocation,
            ],
            stdout=subprocess.PIPE,
            cwd=workDirectory,
            timeout=config["testTimeout"],
        )

        with open(workDirectory + "/stdout.log", "a+") as f:
            f.write(result.stdout.decode("utf-8"))
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

    def createDirectory(self, path, testId=None):
        if testId == None:
            fullpath = path
        else:
            fullpath = path + "/" + str(testId)
        if pathlib.Path(fullpath).mkdir(parents=True, exist_ok=True) is None:
            return fullpath
        else:
            # TODO Add exception
            return False


    def prepareDirectory(self, XML, data, config):
        self.createDirectory(config["dirs"]["resultsDir"])
        testId = data.test_id
        current_test_directory = self.createDirectory(config["dirs"]["resultsDir"], testId)
        self.saveTestNGXML(current_test_directory, XML)
        return testId

    def startPipeline(self, testId, config):
        # TODO move to s3, add exceptions
        current_test_directory = config["dirs"]["resultsDir"] + "/" + str(testId)
        xmlLocation = current_test_directory + "/testng.xml"
        self.runJars(xmlLocation, config, current_test_directory)
        reportResult = self.generateAllureReport(config, testId, current_test_directory)
        # self.callBackFunction(reportResult)
        return testId

    def initTestNg(self, data, config):
        targetPartitionUnit = ""
        extension = data.extension  # ? data.extension : ""
        methods = ""

        try:
            classes = config["testSuites"][data.test_suite]
            # TODO Add catch exceptions

            for method in classes["methods"]:
                method = method["name"]
                methods += f'<include name="{method}" />\n'

            include = f"""<class name="{classes["name"]}">
                        <methods>
                            {methods}
                        </methods>
                    </class>"""

            xml = f"""<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE suite SYSTEM "http://testng.org/testng-1.0.dtd">
        <suite name="RCV">
            <parameter name="hub" value="{data.ptd_address}" />
            <parameter name="url" value="{data.url}" />
            <test name="MainFlow">
                <parameter name="phoneOrEmail" value="{data.phone_or_email}" />
                <parameter name="extension" value="{extension}" />

                <parameter name="password" value="{data.password}" />
                <parameter name="pstnPhoneOrEmail" value="{data.phone_or_email}" />
                <parameter name="pstnExtension" value="{extension}" />
                <parameter name="pstnPassword" value="{data.password}" />

                <parameter name="dialInNumber" value="16504191505" />
                <!-- <parameter name="targetPartition" value="{targetPartitionUnit}" /> -->

                <classes>
                    {include}
                </classes>
            </test>
        </suite>"""
            return xml
        except:
            return False


if __name__ == "__main__":
    parser = YamlParser()
    config = parser.parse("adapter/adapter.yaml")
