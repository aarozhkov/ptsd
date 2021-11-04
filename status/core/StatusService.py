from datetime import datetime, timedelta
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from prometheus_client import Counter
from pydantic.main import BaseModel
from pytz import UTC
import copy

# from models.tests import ReportResponse, ResultEnum, TestResult
from shared.models.task import TestResult
from status.storages.base import ReportStorageCRUD

TEST_COUNT = Counter(
    "ptl_test_result_count_total",
    "This metric collects the all test results from all RCV units, partitions, brands, locations and etc",
    ["partition", "unit", "brand", "location", "test", "outcome"],
)


def check_expiration(test_date: datetime, expiration: int) -> bool:
    return (
        datetime.now().replace(tzinfo=UTC) - timedelta(minutes=expiration) < test_date
    )


class StatusServiceException(Exception):
    """Named exception"""


class TestList(BaseModel):
    reports: List[TestResult]


class StatusService:
    # TODO:
    def __init__(
        self,
        storage: ReportStorageCRUD,
        maxtests: int = 1000,
        # max_results_per_category: int = 3,
        # report_expiration: int = 60,
    ):
        self.storage = storage
        self.maxtests = maxtests
        self.default_pagination = 100

        # Legacy. Probably must be hardcoded due no usage
        # self.max_results_per_category = max_results_per_category
        # self.report_expiration = report_expiration

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

    def get_legacy_report(  # FIXME: refactor to sort with backend storage
        self,
        group_order: List[str],
        status: Optional[ResultEnum] = None,
        view_all: Optional[bool] = False,
    ) -> ReportResponse:
        """Generate report struct"""
        # TODO actual report grouping can't be declaread static Type=). Should be converted
        rcv = {"status": ""}
        for test in self.tests:
            pointer = rcv
            for category in group_order:
                value = getattr(test, category)
                if value in pointer.keys():
                    pointer = pointer[value]
                else:
                    pointer[value] = {}
                    pointer = pointer[value]
                    pointer["status"] = ""
            if status and test.outcome.status.value != status and not view_all:
                continue
            if len(pointer) + 1 >= self.max_results_per_category and not view_all:
                continue
            if any(
                [
                    check_expiration(test.date_time, self.report_expiration),
                    not view_all,
                ]
            ):
                continue

            pointer[test.outcome.test_id] = {
                "timestamp": test.date_time.isoformat(),
                "allure": test.allure_link,
                "log": test.log_link,
                "status": test.outcome.status.value,
            }
        self._set_statuses(rcv)

        return ReportResponse(success=True, groupBy=".".join(group_order), rcv=rcv)

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
            if child_status in ["GREEN", ResultEnum.passed.value]:
                passed_test = +1
            if child_status == ResultEnum.failed.value:
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


status_service = StatusService()


async def report_request_verification(
    groupBy: Optional[str] = None,
    status: Optional[ResultEnum] = None,
    view: Optional[str] = None,
):
    if not groupBy:
        groupBy = DEFAULT_GROUPING
    group_order = groupBy.split(".")
    for group in group_order:
        if group not in ["brand", "partition", "unit", "location", "test"]:
            raise HTTPException(
                status_code=400, detail=f"Not valid group name: {group}"
            )
    if view and view != "all":
        raise HTTPException(status_code=400, detail="view can be only equal 'all'")
    return {"group_order": group_order, "status": status, "view_all": view}


router = APIRouter(tags=["status"])


@router.get("/api/v1/tests")
async def get_tests():
    return status_service.get_tests()


@router.get("/status-json", response_model=ReportResponse)
async def get_status_json(query: dict = Depends(report_request_verification)):
    return status_service.get_report(**query)


@router.post("/api/v1/test-report")
async def add_test(test: TestResult):
    return await status_service.add_test_result(test)
