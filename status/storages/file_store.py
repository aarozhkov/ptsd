from os.path import exists
from typing import Dict, List, Optional

from pydantic import BaseModel
import aiofiles

from models.tests import TestResult
from .base import ReportStorageCRUD


class ResultList(BaseModel):
    """need only for save/load"""

    results: List[TestResult]


class FileReportStorage(ReportStorageCRUD):
    def __init__(self, storage_file="./results"):
        self.storage = storage_file
        self.cached_reports: List[TestResult] = self._get_reports()

    async def get_field_values(self, field: str) -> List[str]:
        """Get all values from Test reports property"""
        result = set()
        for test_result in self.cached_reports:
            result.add(test_result.dict()[field])
        return list(result)

    async def get_by_filters(
        self, filters: Optional[Dict[str, str]] = None, sorted: Optional[List[str]] = None
    ) -> List[TestResult]:  # TODO add more strict type hinting
        """Get reports by props filter"""
        if not filters:
            return self.cached_reports
        # filter = {
        #     prop: props[prop]
        #     for prop in props.keys()
        #     if prop in ["brand", "partition", "unit", "location", "test"]
        # }
        result = []
        skip = False
        for report in self.cached_reports:
            for name, value in report:
                if name in props.keys() and value != props[name]:
                    skip = True
                    continue
            # for key in filter.keys():
            #     if getattr(report, key) != filter[key]:
            #         continue
            if not skip:
                result.append(report)
        return result

    async def get_by_id(self, test_id: int) -> TestResult:
        """get single test result by provided id"""

    async def add(self, report: TestResult) -> bool:  # TODO Add meanfull message
        """Add new test report to storage"""

    def _get_reports(self) -> List:
        """Cache in memory"""
        if not exists(self.storage):
            return []
        with open(self.storage, mode="r") as f:
            content = ResultList.parse_raw(f.read())
        return content.results
        # return [TestResult.parse_obj(test) for test in json.loads(content)]

    async def find(
        self, props: Optional[Dict[str, str]]
    ) -> List:  # TODO add more strict type hinting
        pass

    async def add(self, report: TestResult) -> bool:
        """Add new report to cached store and sync with undernith file
        Duplication check and update are not implemented.
        """
        self.cached_reports.append(report)
        synced = await self._sync_storage()
        return synced

    async def _sync_storage(self) -> bool:
        # json_object = [result.dict() for result in self.cached_reports]
        report_list = ResultList(results=self.cached_reports)
        async with aiofiles.open(self.storage, mode="w") as f:
            await f.write(report_list.json())
            # await f.write(json.dumps(json_object))
        return True

    async def get_field_values(self, field: str) -> List[str]:
        """Get all values from Test reports property"""
