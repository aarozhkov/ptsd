import pathlib
import re
import subprocess
from typing import Dict, Optional, Union
from uuid import UUID

from pydantic import BaseModel

# from adapter.core.filestorage import FileStorage
from shared.core.log import Log
from shared.core.yamlparser import YamlParser

log = Log("DEBUG")

# TODO: Do we need to set it on config level?
# TODO: Do we need to validate it?
TWOUSERS_SCENARIO_NG = """
<!DOCTYPE suite SYSTEM "http://testng.org/testng-1.0.dtd">
<suite name="RCV">
  <parameter name="url" value="CHANGEME_URL" />
  <parameter name="hub" value="CHANGEME_HUB" />
  <test name="MainFlow">
    <parameter name="phoneOrEmail" value="CHANGEME_USER" />
    <parameter name="extension" value="CHANGEME_USER_EXT" />
    <parameter name="password" value="CHANGEME_PASSWORD" />
    <parameter name="pstnPhoneOrEmail" value="CHANGEME_USER" />
    <parameter name="pstnExtension" value="CHANGEME_USER_EXT" />
    <parameter name="pstnPassword" value="CHANGEME_PASSWORD" />
    <parameter name="dialInNumber" value="16504191505" />
    <parameter name="targetPartition" value="" />
    <classes>
      <class name="com.ringcentral.vlt.acceptance.tests.MainFlowTest">
        <methods>
          <include name="twoUsersAreAbleToSeeEachOther_p2pOff" />
        </methods>
      </class>
    </classes>
  </test>
</suite>
"""


class AdapterTestRunException(Exception):
    """Any errors on tests run processing"""


class AdapterResultException(Exception):
    """Any errors on tests results processing"""


def _sunitaze_bool(word: str) -> Union[str, None]:
    return None if word in ["null", "none"] else word


def parse_rcv_call_id(call_id: str) -> tuple:
    try:
        unit = call_id.split("!")[1]
        partition = unit.split("@")[1]
        return partition, unit
    except IndexError:
        return None, None


def parse_testng_output(
    output: str, test: str = "twoUsersAreAbleToSeeEachOther_p2pOff"
) -> Dict:
    """Extract data from TestNG Output
    RCV UPTC tests only about test: twoUsersAreAbleToSeeEachOther_p2pOff
    Result PASSED only if twoUsersAreAbleToSeeEachOther_p2pOff - PASSED
    Other result -> result = failed

    Return flat struct. Specific to twoUsersAreAbleToSeeEachOther_p2pOff

    """

    test_data_pattern = re.compile(
        r"Test name: (?P<test_suit>\w+), "
        r"Status: (?P<status>\w+), "
        r"Call id: (?P<call_id>\S+), "
        r"Reason: (?P<reason>\w+.*)"
    )
    for line in output.split("\n"):
        matched = test_data_pattern.match(line)
        if not matched:
            continue
        # if matched.group("test_suit") == test:
        #     # FIXME: if call_id notation will change - we got wrong unit/partition for SUCCESS tests
        unit, partition = parse_rcv_call_id(matched.group("call_id"))
        return dict(
            status=matched.group("status"),
            unit=unit,
            partition=partition,
            reason=_sunitaze_bool(matched.group("reason")),
        )
    return {
        "status": "FAILED",
        "unit": None,
        "partition": None,
        "reason": f"Cant find result for {test} in output.",
    }


class RunConfig(BaseModel):
    base_path: str = "/app"
    binary_path: str = "binary"
    results_path: str = "results"
    run_location: str
    report_url: str


class RunDataContainer(BaseModel):
    target_url: str
    user_id: str
    user_ext: Optional[str] = None
    password: str
    runner: str  # PTD
    binary_version: str  # exact att jar version for RWC version


class TaskRun:
    def __init__(
        self,
        config: RunConfig,
        test_data: RunDataContainer,
        test_id: UUID,
        test_suite: str = "twoUsersAreAbleToSeeEachOther_p2pOff",
    ) -> None:
        self.config = config
        self.test_id = test_id
        self.data = test_data
        self.test_suite = test_suite
        self._gen_test_directory()
        self._testng_xml = self._gen_testng_config()

    def _gen_test_directory(self):
        # All test run artifacts will be saved in results path for this test.
        try:
            self._test_directory = pathlib.Path(self.config.base_path).joinpath(
                self.config.results_path, str(self.test_id)
            )
            self._test_directory.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:  # FIXME catch only pathlib exceptions. Check traceback is full
            raise AdapterTestRunException(
                "Cant create result direcory for test: {}, with error: {}".format(
                    self._test_directory, e
                )
            )

    def _gen_testng_config(self):
        return f"""<!DOCTYPE suite SYSTEM "http://testng.org/testng-1.0.dtd">
        <suite name="RCV">
            <parameter name="url" value="{self.data.target_url}" />
            <parameter name="hub" value="{self.data.runner}" />
            <test name="MainFlow">
                <parameter name="phoneOrEmail" value="{self.data.user_id}" />
                <parameter name="extension" value="{self.data.user_ext or ""}" />

                <parameter name="password" value="{self.data.password}" />
                <parameter name="pstnPhoneOrEmail" value="{self.data.user_id}" />
                <parameter name="pstnExtension" value="{self.data.user_ext or ""}" />
                <parameter name="pstnPassword" value="{self.data.password}" />

                <parameter name="dialInNumber" value="16504191505" />
                <parameter name="targetPartition" value="" />

                <classes>
                  <class name="com.ringcentral.vlt.acceptance.tests.MainFlowTest">
                    <methods>
                      <include name="{self.test_suite}" />
                    </methods>
                  </class>
                </classes>
            </test>
        </suite>"""


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
            [
                "allure",
                "generate",
                f"{workDirectory}/target/allure-results",
                "-o",
                f"{workDirectory}/allure",
            ],
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
        # FIXME, stdout pipe to python script.
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
        # TODO: check exit code on test run.
        test_result = _parse_test_output(result.stdout.decode("utf-8"))
        if not test_result:
            test_result = dict(
                test_name=None,
                status="FAILURE",
                call_id=None,
                reason="Can't read Java TestNG output",
            )
        with open(workDirectory + "/stdout.log", "a+") as f:
            f.write(result.stdout.decode("utf-8"))
            f.close()
        return test_result

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
        current_test_directory = self.createDirectory(
            config["dirs"]["resultsDir"], testId
        )
        self.saveTestNGXML(current_test_directory, XML)
        return testId

    def startPipeline(self, testId, config):
        # TODO move to s3, add exceptions
        current_test_directory = config["dirs"]["resultsDir"] + "/" + str(testId)
        xmlLocation = current_test_directory + "/testng.xml"
        test_run_result = self.runJars(xmlLocation, config, current_test_directory)
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
