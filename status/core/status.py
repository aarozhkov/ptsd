from datetime import datetime, timedelta
from typing import Dict, List, Optional

from fastapi.exceptions import HTTPException
from prometheus_client import Counter
from pytz import UTC
import copy
from status.config import StatusSettings

from shared.models.task import TestResult
from status.storages.base import ReportStorageCRUD
from status.storages.sql_store import SQLStorageCRUD
import logging

logger = logging.getLogger(__name__)

TEST_COUNT = Counter(
    "ptl_test_result_count_total",
    "This metric collects the all test results from all RCV units, partitions, brands, locations and etc",
    ["partition", "unit", "brand", "location", "test", "outcome"],
)


def check_expiration(test_date: datetime, expiration: int) -> bool:
    print(
        "This is delta: ",
        datetime.utcnow().replace(tzinfo=UTC) - timedelta(minutes=expiration),
        "test date",
        test_date,
        "result:",
        datetime.utcnow().replace(tzinfo=UTC) - timedelta(minutes=expiration)
        > test_date,
    )
    return (
        datetime.utcnow().replace(tzinfo=UTC) - timedelta(minutes=expiration)
        > test_date
    )


class StatusServiceException(Exception):
    """Named exception"""


class Status:
    # TODO:
    def __init__(
        self,
        storage: ReportStorageCRUD,
        maxtests: int = 1000,
        max_results_per_category: int = 3,
        report_expiration: int = 60,
    ):
        self.storage = storage
        self.maxtests = maxtests
        self.default_pagination = 100

        # Legacy. Probably must be hardcoded due no usage
        self.max_results_per_category = max_results_per_category
        self.report_expiration = report_expiration

    async def add_test_result(self, test: TestResult) -> TestResult:
        # TODO do we need max test limitation?
        # TODO how we should clear test data?
        result = await self.storage.add(test)
        TEST_COUNT.labels(
            partition=test.partition,
            unit=test.unit,
            brand=test.brand,
            location=test.location,
            test=test.test_suit,
            outcome=test.status,
        ).inc()
        return result

    async def report(
        self,
        filters: Optional[Dict] = {},
        page_num: Optional[int] = 0,
        page_limit: Optional[int] = None,
    ) -> List[TestResult]:
        if not page_limit:
            page_limit = self.default_pagination
        return await self.storage.get_by_filters(
            filters=filters, page_limit=page_limit, page_offset=page_limit * page_num
        )

    async def _reqursive_grouping(
        self, created_filters: Dict[str, str], group_order: Dict
    ):
        """recursion report grouping for legacy report v2"""
        if not group_order:
            # FIXME: This is a lot of separate requests to DB.
            return await self.storage.get_by_filters(
                filters=created_filters, page_limit=3
            )
        result = {}
        group = copy.deepcopy(group_order)
        field, values = group.popitem()
        for value in values:
            result[value] = self._reqursive_grouping(
                {**filters, **{field: value}}, group
            )

        return result

    def get_legacy_report_v2(self):
        """Legacy report implementation with out pointers magic"""

    async def get_legacy_report(  # FIXME: refactor to sort with backend storage
        self,
        group_order: List[str],
        status: Optional[str] = None,
        view_all: Optional[bool] = False,
    ) -> dict:
        """Generate report struct"""
        # TODO actual report grouping can't be declaread static Type=). Should be converted
        tests: List[TestResult] = await self.storage.get_by_filters()
        rcv = {"status": ""}
        for test in tests:
            pointer = rcv
            for category in group_order:
                value = getattr(test, category)
                if value in pointer.keys():
                    pointer = pointer[value]
                else:
                    pointer[value] = {}
                    pointer = pointer[value]
                    pointer["status"] = ""
            if status and test.status != status and not view_all:
                continue
            if len(pointer) + 1 >= self.max_results_per_category and not view_all:
                continue
            if any(
                [
                    check_expiration(test.date_time, self.report_expiration),
                    view_all,
                ]
            ):
                continue

            pointer[test.test_id] = {
                "timestamp": test.date_time.isoformat(),
                "allure": test.allure_link,
                "log": test.log_link,
                "status": test.status,
            }
        self._set_statuses(rcv)

        return dict(success=True, groupBy=".".join(group_order), rcv=rcv)

    def _set_statuses(self, report: dict) -> str:
        if report["status"]:
            return report["status"]
        status = "GREEN"
        failed_test = 0
        passed_test = 0
        for child in report:
            if child == "status":
                continue
            child_status = self._set_statuses(report[child])
            # if child_status in ["GREEN", ResultEnum.passed.value]:
            if child_status in ["GREEN", "PASSED"]:
                passed_test = +1
            if child_status == "FAILED":
                failed_test = +1
            if child_status in ["YELLOW", "RED"]:
                status = child_status
        if status != "GREEN":
            report["status"] = status
            return status
        if failed_test >= self.max_results_per_category:
            status = "RED"
        if failed_test > 0:
            status = "YELLOW"
        if passed_test == 0:
            status = "GRAY"
        report["status"] = status
        return status


status_service = Status(storage=SQLStorageCRUD(), **StatusSettings().dict())


# FIXME raise StatusServiceException instead of HTTPException
#       regestry Status service exception in fastapi
async def report_request_verification(
    groupBy: str = "partition.unit.brand.location.test",
    status: Optional[str] = None,
    # status: Optional[ResultEnum] = None,
    view: Optional[str] = None,
):
    group_order = groupBy.split(".")
    for i, group in enumerate(group_order):
        if group not in ["brand", "partition", "unit", "location", "test", "test_suit"]:
            raise HTTPException(
                status_code=400, detail=f"Not valid group name: {group}"
            )
        if group == "test":
            group_order[i] = "test_suit"
    if view and view != "all":
        raise HTTPException(status_code=400, detail="view can be only equal 'all'")
    return {"group_order": group_order, "status": status, "view_all": view}
