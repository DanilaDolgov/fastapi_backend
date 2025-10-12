import json
from typing import List, Dict

from fastapi import APIRouter
from fastapi_cache.decorator import cache
from pydantic import BaseModel

from src.dependencies.dependencies import DBDep
from src.schemas.facilities import FacilitiesRequest
from src.utils.decorator_cache import redis_cache
from src.tasks.tasks import test_task

router_facilities = APIRouter(prefix="/facilities", tags=["Удобства"])


@router_facilities.get("")
# @redis_cache(ttl=60)
@cache(expire=60)
async def get_all_facilities(db: DBDep) -> List:
    facility = await db.facilities.get_all()
    return facility


    # facilities_from_cache = await redis_manager.get("facilities")
    # print(facilities_from_cache)
    # if facilities_from_cache:
    #     return json.loads(facilities_from_cache)
    # else:
    #     facilities = await db.facilities.get_all()
    #     facilities_schema = [facility.model_dump() for facility in facilities]
    #     await redis_manager.set("facilities", json.dumps(facilities_schema))
    #     return facilities


@router_facilities.post("")
async def add_facilities(db:DBDep, data_facilities: FacilitiesRequest) -> dict:
    facilities = await db.facilities.add(data_facilities)
    await db.commit()
    # test_task.delay("привет celery")

    return {'Status': 'Ok', 'facilities': facilities}


