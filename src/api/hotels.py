from datetime import date
from fastapi import Query, APIRouter, Body, HTTPException

from src.dependencies.dependencies import DBDep, Pagination
from src.exceptions import NotCorrectDateException, ObjectNotFoundException
from src.schemas.hotels import HotelPATCH, HotelAdd
from src.dependencies.dependencies import hotel_not_none
from src.services.hotels import HotelServices

router_hotels = APIRouter(prefix="/hotels", tags=["Отели"])


@router_hotels.get("")
async def get_hotels(
    pagination: Pagination,
    db: DBDep,
    date_to: date,
    date_from: date,
    title: str | None = Query(None, description="Название отеля"),
    location: str | None = Query(None, description="Адрес отеля"),
):
    try:
        hotels = await HotelServices(db).get_filtered_by_time(pagination=pagination,
                                                              date_to=date_to,
                                                              date_from=date_from,
                                                              title=title,
                                                              location=location)
    except NotCorrectDateException as ex:
        raise HTTPException(status_code=400, detail=ex.detail)
    return {"Status": "Ok", "data": hotels}

@router_hotels.delete("/{hotel_id}")
async def delete_hotels(db: DBDep, hotel_id: int):
    await HotelServices(db).delete_hotels(hotel_id=hotel_id)

    return {"Status": "Ok"}


@router_hotels.get("/{hotel_id}")
async def get_hotel_one(db: DBDep, hotel_id: int, hnn: hotel_not_none):
    if hnn:
        hotel = HotelServices(db).get_one(hotel_id=hotel_id)

        return {"Status": "Ok", "data": hotel}


@router_hotels.post("")
async def create_hotels(
    db: DBDep,
    data_hotel: HotelAdd = Body(
        openapi_examples={
            "1": {
                "summary": "Sochi",
                "value": {"title": "Sochi", "location": "ул. Лазурная дом 1"},
            }
        }
    ),
):
    hotel = await HotelServices(db).add_hotel(data_hotel=data_hotel)

    return {"Status": "Ok", "data": hotel}


@router_hotels.put("/{hotel_id}")
async def update_hotel(db: DBDep, hotel_id: int, data_hotel: HotelAdd):
    await HotelServices(db).update_hotel(hotel_id=hotel_id, data_hotel=data_hotel)

    return {"Status": "Ok"}


@router_hotels.patch("/{hotel_id}")
async def update_patch_hotel(db: DBDep, hotel_id: int, data_hotel: HotelPATCH):
    await HotelServices(db).update_patch_hotel(data_hotel=data_hotel, hotel_id=hotel_id)

    return {"Status": "Ok"}
