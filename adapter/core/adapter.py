import pathlib
import subprocess
import os.path
import shutil
import httpx
import asyncio

from shared.core.yamlparser import YamlParser
from shared.core.log import Log
from adapter.core.filestorage import FileStorage

log = Log("DEBUG")


class Adapter:
    def __init__(self, config):
        self.config = config

    def buildJars(self):
        return True

    def readinessProbe(self):
        return True

    def getAllureReport(self, testId):
        return True

    def getTestLog(self, testId):
        return True

    def clearResultDir(self, workDirectory):
        try:
            shutil.rmtree(workDirectory)
            return True
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))
            return False

    def generateAllureReport(self, testId, workDirectory):
        result = subprocess.run(
            ["allure", "generate",
                f"{workDirectory}/target/allure-results", "-o", f"{workDirectory}/allure"],
            stdout=subprocess.PIPE,
            cwd=workDirectory,
            timeout=self.config["testTimeout"],
        )
        with open(workDirectory + "/stdout.log", "a+") as f:
            f.write(result.stdout.decode("utf-8"))
            f.close()

        try:
            allureReportIndex = pathlib.Path(
                workDirectory + "/allure/index.html")
            allureReportIndex.resolve(strict=True)
        except FileNotFoundError:
            log.error("FileNotFoundError: allure problem")
            return ""
        else:
            log.debug("Allure OK. Try Upload to s3")
            fs = FileStorage(self.config)
            reportUrl = fs.upload_directory(workDirectory, testId)
            return reportUrl

    def runJars(self, XMLLocation, workDirectory):
        buildsDirectory = self.config["dirs"]["buildsDir"]
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
            timeout=self.config["testTimeout"],
        )

        with open(workDirectory + "/stdout.log", "a+") as f:
            f.write(result.stdout.decode("utf-8"))
            f.close()
        return True

    def saveTestNGXML(self, tests_directory: str, XML: str):
        # TODO add exceptions
        xmlLocation = tests_directory + "/testng.xml"

        try:
            with open(xmlLocation, "w+") as f:
                f.write(XML)
                f.close()
        except OSError:
            log.error(f"Could not open/read file: (fname)")
        return xmlLocation

    def callBackFunction(self, taskId, result, url=None):
        log.debug("Try callback")
        payload = {"task": taskId, "result": result}
        try:
            httpx.post(self.config["callBackURL"], data=payload)
        except TimeoutError as err:
            log.error(err)
        except asyncio.TimeoutError as err:
            log.error(err)
        except httpx.ConnectTimeout as err:
            log.error(err)
        except httpx.HTTPError as err:
            log.error(err)
        except Exception as e:
            log.error(e)
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

    def prepareDirectory(self, XML, data):
        self.createDirectory(self.config["dirs"]["resultsDir"])
        testId = data.test_id
        current_test_directory = self.createDirectory(
            self.config["dirs"]["resultsDir"], testId)
        self.saveTestNGXML(current_test_directory, XML)
        return testId

    def startPipeline(self, testId):
        current_test_directory = self.config["dirs"]["resultsDir"] + \
            "/" + str(testId)
        xmlLocation = current_test_directory + "/testng.xml"
        try:
            self.runJars(xmlLocation, current_test_directory)
            result = self.generateAllureReport(testId, current_test_directory)
            self.callBackFunction(testId, result)
            self.clearResultDir(current_test_directory)
        except Exception as e:
            self.callBackFunction(testId, False)
            self.clearResultDir(current_test_directory)
        return testId

    def initTestNg(self, data):
        targetPartitionUnit = ""
        extension = data.extension  # ? data.extension : ""
        methods = ""

        try:
            classes = self.config["testSuites"][data.test_suite]
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
