from typing import Dict, List, Optional, Protocol, runtime_checkable

from shared.models.task import TestResult


@runtime_checkable
class ReportStorageCRUD(Protocol):
    async def get_field_values(self, fields: List[str]) -> Dict[str, List]:
        """Get all values from Test reports property"""

    async def get_by_filters(
        self,
        order_by: Optional[List[str]] = None,
        filters: Optional[Dict[str, str]] = {},
        page_limit: int = 0,
        page_offset: int = 0,
    ) -> List[TestResult]:
        """Get reports by props filter"""

    async def get_by_id(self, test_id: int) -> TestResult:
        """get single test result by provided id"""

    async def add(self, report: TestResult) -> TestResult:
        """Add new test report to storage"""


# FIXME for generic BASECRUD

#     async def create(self, schema, *args, **kwargs) -> Optional[CreateSchemaType]:
#         obj = await self.model.create(**schema.dict(exclude_unset=True), **kwargs)
#         return await self.get_schema.from_tortoise_orm(obj)

#     async def update(self, schema, **kwargs) -> Optional[UpdateSchemaType]:
#         await self.model.filter(**kwargs).update(**schema.dict(exclude_unset=True))
#         return await self.get_schema.from_queryset_single(self.model.get(**kwargs))

#     async def delete(self, **kwargs):
#         obj = await self.model.filter(**kwargs).delete()
#         if not obj:
#             raise HTTPException(status_code=404, detail='Object does not exist')

#     async def all(self) -> Optional[GetSchemaType]:
#         return await self.get_schema.from_queryset(self.model.all())

#     async def filter(self, **kwargs) -> Optional[GetSchemaType]:
#         return await self.get_schema.from_queryset(self.model.filter(**kwargs))

#     async def get(self, **kwargs) -> Optional[GetSchemaType]:
#         return await self.get_schema.from_queryset_single(self.model.get(**kwargs))

#     async def get_obj(self, **kwargs) -> Optional[ModelType]:
#         return await self.model.get_or_none(**kwargs)
