from datetime import datetime

import pytest
import pytz
from prometheus_client import REGISTRY

from models.tests import ReportResponse, TestResult
from services.status import StatusService, group_by_category


@pytest.fixture
def test_timestamp():
    return datetime.utcnow().replace(tzinfo=pytz.utc)


@pytest.fixture
def test_range():
    tests = [
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
    result = []
    for test in tests:
        result.append(TestResult.parse_obj(test))
    return result


@pytest.fixture
def test_report():
    return {
        "success": True,
        "groupBy": "partition.unit.brand.location.test",
        "rcv": {
            "status": "GREEN",
            "eu-02": {
                "status": "GREEN",
                "eu-02-fra01": {
                    "status": "GREEN",
                    "ATOS": {
                        "status": "GREEN",
                        "FRA01": {
                            "status": "GREEN",
                            "twoUsersAreAbleToSeeEachOther_p2pOff": {
                                "status": "GREEN",
                                "2": {
                                    "status": "PASSED",
                                    "timestamp": "2021-10-06T09:14:05.480000+00:00",
                                    "allure": "link",
                                    "log": "log_link",
                                },
                            },
                        },
                    },
                },
            },
            "us-09": {
                "status": "GREEN",
                "us-09-sjc01": {
                    "status": "GREEN",
                    "RC": {
                        "status": "GREEN",
                        "SJC01": {
                            "status": "GREEN",
                            "twoUsersAreAbleToSeeEachOther_p2pOff": {
                                "status": "GREEN",
                                "1": {
                                    "status": "PASSED",
                                    "timestamp": "2021-10-07T09:14:05.480000+00:00",
                                    "allure": "link",
                                    "log": "log_link",
                                },
                            },
                        },
                    },
                },
            },
        },
    }


def test_status_defaults():
    service = StatusService()
    assert service.tests == []
    assert service.maxtests == 1000
    assert service.max_results_per_category == 3
    assert service.report_expiration == 60


def test_status_configured(test_range):
    service = StatusService(
        entry_tests=test_range,
        maxtests=10,
        max_results_per_category=4,
        report_expiration=10,
    )
    assert all(test in service.tests for test in test_range)
    assert service.maxtests == 10
    assert service.max_results_per_category == 4
    assert service.report_expiration == 10


def test_clean_status_report():
    clean_status = StatusService(entry_tests=[])
    expected_report = ReportResponse(
        success=True,
        groupBy="partition.unit.brand.location.test",
        rcv={"status": "GRAY"},
    )
    actual_report = clean_status.get_report(
        group_order=expected_report.groupBy.split(".")
    )
    # expect default groups if not set in request
    assert actual_report.groupBy == "partition.unit.brand.location.test"
    assert expected_report == actual_report


def test_filled_status_report_no_time_boundries(test_range, test_report):
    status = StatusService()
    for test in test_range:
        status.add_test_result(test)
    expected_report = ReportResponse.parse_obj(test_report)
    actual_report = status.get_report(
        group_order=expected_report.groupBy.split("."), view_all=True
    )
    # expect default groups if not set in request
    assert actual_report.groupBy == "partition.unit.brand.location.test"
    assert expected_report == actual_report


def test_service_add_test_result(test_range):
    service = StatusService(entry_tests=[])
    service.add_test_result(test_range[0])
    labels = dict(
        partition=test_range[0].partition,
        unit=test_range[0].unit,
        brand=test_range[0].brand,
        location=test_range[0].location,
        test=test_range[0].test,
        outcome=test_range[0].outcome.status.value,
    )
    first_metric = REGISTRY.get_sample_value(
        "ptl_test_result_count_total", labels=labels
    )
    assert first_metric is not None
    assert len(service.tests) == 1
    service.add_test_result(test_range[0])
    second_metric = REGISTRY.get_sample_value(
        "ptl_test_result_count_total", labels=labels
    )
    assert len(service.tests) == 2
    assert second_metric - first_metric == 1


def test_group_by_partition(test_range):
    result = group_by_category("partition", test_range)
    assert isinstance(result, dict)
    assert all(part in result.keys() for part in ["eu-02", "us-09"])


def test_group_by_brand(test_range):
    result = group_by_category("brand", test_range)
    assert isinstance(result, dict)
    assert all(brand in result.keys() for brand in ["RC", "ATOS"])


def test_group_by_location(test_range):
    result = group_by_category("location", test_range)
    assert isinstance(result, dict)
    assert all(location in result.keys() for location in ["SJC01", "FRA01"])


def test_by_category(test_range):
    result = group_by_category("unit", test_range)
    assert all(unit in result.keys() for unit in ["us-09-sjc01", "eu-02-fra01"])

    result = group_by_category("test", test_range)
    assert "twoUsersAreAbleToSeeEachOther_p2pOff" in result.keys()
