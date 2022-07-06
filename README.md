# Contributing

* Repository uses fast-forward merges
* Each commit title starts with jira task number e.g. RCV-123321: Introduce new bugs

  (this implicitly allows you to violate 50 symbols limit for commit title)

* Commit titles are imperative
* Single commit represents atomic change in code 
* Squashing commits is encouraged
---
**Reminder**

Don't forget to write an unit test for new functionality introduced!
---
## Sources
See https://chris.beams.io/posts/git-commit/ for commits best practices

See https://trunkbaseddevelopment.com/ for details on trunk-based development




# AAT(automated acceptance test) UPTC adapter

TODO: link to aat repo

UPTC branch contains tests with simple e2e scenarios for RCV:

* twoUsersAreAbleToSeeEachOther_p2pOff
* checkPstnParticipantInConference - Does not work 
* checkClosedCaptionsRecognitionInConference - Does not work

But UPTC will run only 1 test twoUsersAreAbleToSeeEachOther_p2pOff
Other tests not work right now.


UPTC runner MUST have single - summarized boolean result.
If we got several tests we need summarized data for all tests.



### Entry data:

* login
* password
* extension if needed
* deal-in number for pstn checks(not worked)


### Output:

* Allure report: ./target/allure-reports
* jar run output. Catch all output. Parse only 3 scenarios:
  * test configuration failure. Possibly issues with config preparation
  * test run failed because of system under test
  * test run positive(success)


### Algoritm:

1. Get entry data
2. Generate testng.xml
3. run testng jar 
4. parse output - for result
5. save output as artifact
6. generate Allure report from /target/allure/reports
7. save allure output to output artifact

Step 3 and step 6 should be run in separate containers?

### POD?

1. Manage container - python code to fetch and run jobs, get and upload results.
2. TestNG JAR code sycnronizer? Down load and put in POD shared location actual JAR code
3. Allure container?

* Q. How to make TestNG container and Allure container to be runned forever?
  A. Make shell wrap for that.
* Q. How to update TestNG containers?
  A. Update POD deployment description

### TestNG JAr as S3 artifact
Python managment will check and upload required TestNG jar version from remote repo.
Test will fail if required versions is not available
Python will cache last 3 versions of TestNG Jar


Separate workflow for buiuld and upload testng jars to S3

### Use workflows

Argo workflow or tekton.
This is template based pipelines with can be run/triggered by some events.
pipeline consist of stages with(DAG dependancy).
Steps represent container run. Container must be prepared
Workfow can share data between steps.

Algorithm:

1. Some job get scheduled task and triggers event
2. Event contains all entry data.
3. Workflow. Step1: generate testng.xml
3. Workflow. Step2(which image to run - depends on step1): run TestNG jar with step1 artefact
4. Workflow. Step3: parse step2 testNG output log
5. Workflow. Step4: generate allure report from step2 artifacts
6. Upload ste3, step4 artifacts to s3 bucket. Send report to report storage



Positive:
```
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
```

NEGATIVE


```
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
```

Configuration fails:
```
SLF4J: Failed to load class "org.slf4j.impl.StaticLoggerBinder".
SLF4J: Defaulting to no-operation (NOP) logger implementation
SLF4J: See http://www.slf4j.org/codes.html#StaticLoggerBinder for further details.

===============================================
RCV
Total tests run: 1, Passes: 0, Failures: 0, Skips: 1
Configuration Failures: 2, Skips: 0
===============================================
```
