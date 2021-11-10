import asyncio
import json
from unittest.mock import MagicMock, mock_open, patch

import pytest

from models.tests import TestResult
from storages.filestorage import FileReportStorage


@pytest.fixture
def report_store(tmp_path):
    report_store = tmp_path / "report"
    report_store.write_text(
        json.dumps(
            {
                "results": [
                    {
                        "test": "twoUsersAreAbleToSeeEachOther_p2pOff",
                        "brand": "RC",
                        "location": "SJC01",
                        "partition": "us-09",
                        "unit": "us-09-sjc01",
                        "allure_link": "link",
                        "log_link": "log_link",
                        "ptr_address": "sjc01-c04-ptr01",
                        "date_time": "2021-10-07T09:14:05.480000+00:00",
                        "outcome": {
                            "test_id": "1",
                            "status": "PASSED",
                            "reason": None,
                            "duration": 78,
                        },
                    },
                    {
                        "test": "twoUsersAreAbleToSeeEachOther_p2pOff",
                        "brand": "ATOS",
                        "location": "FRA01",
                        "partition": "eu-02",
                        "unit": "eu-02-fra01",
                        "allure_link": "link",
                        "log_link": "log_link",
                        "date_time": "2021-10-06T09:14:05.480000+00:00",
                        "ptr_address": "sjc01-c04-ptr01",
                        "outcome": {
                            "test_id": 2,
                            "status": "PASSED",
                            "reason": "hz",
                            "duration": 78,
                        },
                    },
                ]
            }
        )
    )
    return report_store


def test_init_check_given_file_exists():
    with patch("storages.filestorage.exists", MagicMock(return_value=False)) as m:
        filestore = FileReportStorage()
        m.assert_called()
        assert filestore.cached_reports == []


def test_init_read_default_file():
    with patch("storages.filestorage.exists", MagicMock(return_value=True)):
        with patch("builtins.open", mock_open(read_data='{"results": []}')) as m:
            filestore = FileReportStorage()
            m.assert_called_with("./results", mode="r")
            assert filestore.cached_reports == []


def test_load_reports_from_file(report_store):
    filestore = FileReportStorage(storage_file=report_store)
    assert filestore.cached_reports != []
    assert isinstance(filestore.cached_reports[0], TestResult)
    assert filestore.cached_reports[0].brand == "RC"


@pytest.mark.asyncio
async def test_add_test_report(tmp_path):
    test_result_report = TestResult.parse_obj(
        {
            "test": "twoUsersAreAbleToSeeEachOther_p2pOff",
            "brand": "RC",
            "location": "SJC01",
            "partition": "us-09",
            "unit": "us-09-sjc01",
            "allure_link": "link",
            "log_link": "log_link",
            "date_time": "2021-10-07T09:14:05.480000+00:00",
            "ptr_address": "sjc01-c04-ptr01",
            "outcome": {"test_id": 1, "status": "PASSED", "duration": 78},
        }
    )
    report_store = tmp_path / "report"
    report_store.write_text('{ "results": []}')
    storage = FileReportStorage(storage_file=report_store)
    success = await storage.add(test_result_report)
    assert success is True
    assert test_result_report in storage.cached_reports
    assert report_store.read_text() == json.dumps(
        {
            "results": [
                {
                    "test": "twoUsersAreAbleToSeeEachOther_p2pOff",
                    "brand": "RC",
                    "location": "SJC01",
                    "partition": "us-09",
                    "unit": "us-09-sjc01",
                    "allure_link": "link",
                    "log_link": "log_link",
                    "ptr_address": "sjc01-c04-ptr01",
                    "date_time": "2021-10-07T09:14:05.480000+00:00",
                    "outcome": {
                        "test_id": "1",
                        "status": "PASSED",
                        "reason": None,
                        "duration": 78,
                    },
                }
            ]
        }
    )


@pytest.mark.asyncio
async def test_find(report_store):
    storage = FileReportStorage(storage_file=report_store)
    find_by_brand_rc = await storage.find(props={"brand": "RC"})
    assert len(find_by_brand_rc) == 1
    assert find_by_brand_rc[0].brand == "RC"

    find_notexisting_brand = await storage.find(props={"brand": "NOTEXISTS"})
    assert find_notexisting_brand == []


@pytest.mark.asyncio
async def test_get_prop_values(report_store):
    storage = FileReportStorage(storage_file=report_store)
    brands = await storage.get_field_values("brand")
    assert all([brand in ["ATOS", "RC"] for brand in brands])

    locations = await storage.get_field_values("location")
    assert all([location in ["FRA01", "SJC01"] for location in locations])
