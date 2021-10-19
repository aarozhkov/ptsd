from fastapi import APIRouter, Depends
from .status import StatusService


router = APIRouter()


@router.get("/api/v1/di")
# async def get_di():
async def get_di(status: StatusService = Depends()):
    return status.max_results_per_category
