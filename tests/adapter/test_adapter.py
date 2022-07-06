import asyncio
from uuid import uuid4
from xml.dom.minidom import parseString

import pytest

# import adapter.main
from adapter.core.adapter import (RunConfig, RunDataContainer, TaskRun,
                                  parse_testng_output)

# from shared.core.adapter import TestRequest

"""
{
  "version": "0.1",
  "url": "https://v.ringcentral.com",
  "ptd_address": "http://iad41-c04-ptd01:4444",
  "phone_or_email": "14706495518",
  "extension": "101",
  "password": "Test!123",
  "test_suite": "video",
  "notify_on_complete": true,
  "test_id": 111
}
"""


@pytest.fixture
def failed_configuration():
    return """
SLF4J: Failed to load class "org.slf4j.impl.StaticLoggerBinder".
SLF4J: Defaulting to no-operation (NOP) logger implementation
SLF4J: See http://www.slf4j.org/codes.html#StaticLoggerBinder for further details.

===============================================
RCV
Total tests run: 1, Passes: 0, Failures: 0, Skips: 1
Configuration Failures: 2, Skips: 0
===============================================
    """


@pytest.fixture
def failed_test_run():
    return """
SLF4J: Failed to load class "org.slf4j.impl.StaticLoggerBinder".
SLF4J: Defaulting to no-operation (NOP) logger implementation
SLF4J: See http://www.slf4j.org/codes.html#StaticLoggerBinder for further details.
Step: participants initialization
Jan 11, 2022 3:40:19 PM org.openqa.selenium.remote.DesiredCapabilities chrome
INFO: Using `new ChromeOptions()` is preferred to `DesiredCapabilities.chrome()`
Test name: twoUsersAreAbleToSeeEachOther_p2pOff, Status: FAILED, Call id: null, Reason: Could not start a new session. Possible causes are invalid address of the remote server or browser start-up failure.
Build info: version: 'unknown', revision: 'unknown', time: 'unknown'
System info: host: 'LM4VXML85', ip: '10.13.86.12', os.name: 'Mac OS X', os.arch: 'x86_64', os.version: '12.1', java.version: '1.8.0_312'
Driver info: driver.version: RemoteWebDriver

===============================================
FAILED: twoUsersAreAbleToSeeEachOther_p2pOff
REASON: Could not start a new session. Possible causes are invalid address of the remote server or browser start-up failure.
Build info: version: 'unknown', revision: 'unknown', time: 'unknown'
System info: host: 'LM4VXML85', ip: '10.13.86.12', os.name: 'Mac OS X', os.arch: 'x86_64', os.version: '12.1', java.version: '1.8.0_312'
Driver info: driver.version: RemoteWebDriver
===============================================


===============================================
RCV
Total tests run: 1, Passes: 0, Failures: 1, Skips: 0
===============================================
    """


@pytest.fixture
def test_run_success():
    return """
SLF4J: Failed to load class "org.slf4j.impl.StaticLoggerBinder".
SLF4J: Defaulting to no-operation (NOP) logger implementation
SLF4J: See http://www.slf4j.org/codes.html#StaticLoggerBinder for further details.
Step: participants initialization
Jan 10, 2022 10:08:03 PM org.openqa.selenium.remote.DesiredCapabilities chrome
INFO: Using `new ChromeOptions()` is preferred to `DesiredCapabilities.chrome()`
Jan 10, 2022 10:08:08 PM org.openqa.selenium.remote.ProtocolHandshake createSession
INFO: Detected dialect: W3C
Jan 10, 2022 10:08:09 PM org.openqa.selenium.remote.DesiredCapabilities chrome
INFO: Using `new ChromeOptions()` is preferred to `DesiredCapabilities.chrome()`
Jan 10, 2022 10:08:11 PM org.openqa.selenium.remote.ProtocolHandshake createSession
INFO: Detected dialect: W3C
Step: open welcome page
Step: check visibility welcome page (for both agents)
TEST Commit >>>>>>>>>
TEST Commit #2 >>>>>>>>>
Step: sign-in (first participant)
Step: start conference + check conference (first participant)
Meeting ID: 673df471-13d6-44fd-8fd6-ac7d6227fab7!us-02-iad02@us-02
Step: join conference + check (second participant)
Step: check video (for both participants)
Step: end meeting (first participant)
Test name: twoUsersAreAbleToSeeEachOther_p2pOff, Status: PASSED, Call id: 673df471-13d6-44fd-8fd6-ac7d6227fab7!us-02-iad02@us-02, Reason: null

===============================================
PASSED: twoUsersAreAbleToSeeEachOther_p2pOff
===============================================


===============================================
RCV
Total tests run: 1, Passes: 1, Failures: 0, Skips: 0
===============================================

    """


@pytest.fixture
def config_testrun():
    return RunConfig(
        run_location="sjc01", report_url="http://status.ptsd.ringcentral.com"
    )


@pytest.fixture
def testng_xml():
    return """
<!DOCTYPE suite SYSTEM "http://testng.org/testng-1.0.dtd">
<suite name="RCV">
  <parameter name="url" value="https://v.ringcentral.com" />
  <parameter name="hub" value="http://ptd.ptsd.ringcentral.com:4444" />
  <test name="MainFlow">
    <parameter name="phoneOrEmail" value="+1111111111" />
    <parameter name="extension" value="101" />
    <parameter name="password" value="password" />
    <parameter name="pstnPhoneOrEmail" value="+1111111111" />
    <parameter name="pstnExtension" value="101" />
    <parameter name="pstnPassword" value="password" />
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
</suite>"""


@pytest.fixture
def testdata():
    return {
        "phoneOrEmail": "+1111111111",
        "url": "https://v.ringcentral.com",
        "extension": "101",
        "password": "password",
        "hub": "http://ptd.ptsd.ringcentral.com:4444",
        "binary_version": "21.1.30",
    }


def test_parse_uptc_run_success(test_run_success):
    result = parse_testng_output(test_run_success)
    assert result["status"] == "PASSED"


def test_parse_uptc_bad_configuration_test_output(failed_configuration):
    result = parse_testng_output(failed_configuration)
    assert result["status"] == "FAILED"
    assert (
        result["reason"]
        == "Cant find result for twoUsersAreAbleToSeeEachOther_p2pOff in output."
    )


def test_parse_uptc_run_failed(failed_test_run):
    result = parse_testng_output(failed_test_run)
    assert result["status"] == "FAILED"
    assert (
        result["reason"]
        == "Could not start a new session. Possible causes are invalid address of the remote server or browser start-up failure."
    )


def test_run_config(config_testrun):
    assert config_testrun.base_path == "/app"
    assert config_testrun.report_url == "http://status.ptsd.ringcentral.com"


def test_testrun_init(tmpdir, config_testrun, testdata):
    # tmp_dir = "/tmp/pytest"
    # tmp_dir = pytest.TempPathFactory(
    #     given_basetemp=pathlib.Path("/tmp/pytest"), trace="DEBUG"
    # ).mktemp("adapter")
    config_testrun.base_path = tmpdir
    test_data = RunDataContainer(
        target_url=testdata["url"],
        user_id=testdata["phoneOrEmail"],
        user_ext=testdata["extension"],
        password=testdata["password"],
        runner=testdata["hub"],
        binary_version=testdata["binary_version"],
    )
    test_id = uuid4()
    run = TaskRun(config=config_testrun, test_data=test_data, test_id=test_id)

    # Check test result dir was created inside tmp dir
    assert any([str(test_id) in entry.basename for entry in tmpdir.visit()])
    testng_xml = parseString(run._testng_xml)
    # Check data was set correctly in xml
    # TODO need to check whole XML. But there issues with tabs/spaces -
    for element in testng_xml.getElementsByTagName("parameter"):
        if element.getAttribute("name") in testdata.keys():
            assert testdata[element.getAttribute("name")] == element.getAttribute(
                "value"
            )


@pytest.fixture(scope="module")
@pytest.mark.asyncio
async def data():
    data = {
        "version": "0.1",
        "url": "https://v.ringcentral.com",
        "ptd_address": "http://iad41-c04-ptd01:4444",
        "phone_or_email": "14706495518",
        "extension": "101",
        "password": "Test!123",
        "test_suite": "video",
        "notify_on_complete": True,
        "test_id": 0,
    }
    yield data


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


# @pytest.mark.asyncio
# async def test_execute(data):
# validTestRequest = TestRequest(data)
# assert 'RC-Commercial' in accounter.pool.keys()
