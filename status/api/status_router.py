from fastapi import APIRouter, Depends
from ..core.status import status_service, report_request_verification
from shared.models.task import TestResult

router = APIRouter(tags=["status"])


@router.get("/api/v1/tests")
async def get_tests():
    return await status_service.report()


@router.get("/status-json", response_model=dict)
async def get_status_json(query: dict = Depends(report_request_verification)):
    return await status_service.get_legacy_report(**query)


@router.post("/api/v1/test-report")
async def add_test(test: TestResult):
    return await status_service.add_test_result(test)
