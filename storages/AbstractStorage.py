from typing import Dict, List, Optional

from models.tests import TestResult


class AbstractReportStorage:
    async def get_field_values(self, field: str) -> List[str]:
        """Get all values from Test reports property"""

    async def find(
        self, props: Optional[Dict[str, str]]
    ) -> List:  # TODO add more strict type hinting
        """Get reports by props filter"""

    async def add(self, report: TestResult) -> bool:  # TODO Add meanfull message
        """Add new test report to storage"""
