from datetime import date

from fastapi import Query, APIRouter, Body
from src.dependencies.dependencies import DBDep, Pagination
from src.schemas.facilities import FacilitiesRequest, Facilities
from src.repositories.rooms import RoomsRepository

router_facilities = APIRouter(prefix="/facilities", tags=["Удобства"])


@router_facilities.get("")
async def get_all_facilities(db: DBDep):
    return await db.facilities.get_all()


@router_facilities.post("")
async def add_facilities(db:DBDep, data_facilities: FacilitiesRequest):
    facilities = await db.facilities.add(data_facilities)
    await db.commit()

    return {'Status': 'Ok', 'facilities': facilities}


