from datetime import date

from fastapi import Query, APIRouter, Body
from src.database import async_session_maker
from src.dependencies.dependencies import DBDep, Pagination
from src.schemas.hotels import HotelPATCH, HotelAdd
from src.repositories.rooms import RoomsRepository

router_hotels = APIRouter(prefix="/hotels", tags=["Отели"])


@router_hotels.get("/{hotel_id}")
async def get_distinct_rooms_in_hotel(hotel_id: int):
    async with async_session_maker() as session:
        rooms_in_hotel = await RoomsRepository(session).get_in_params(hotel_id=hotel_id)
        return {'Rooms in hotel': rooms_in_hotel}



@router_hotels.get("")
async def get_hotels(
        pagination: Pagination,
        db: DBDep,
        date_to: date,
        date_from: date,
        title: str | None = Query(None, description="Название отеля"),
        location: str | None = Query(None, description="Адрес отеля"),
):
    per_page = pagination.per_page or 5
    return await db.hotels.get_filtered_by_time(date_from=date_from,
                                                date_to=date_to,
                                                title=title,
                                                location=location,
                                                limit=per_page,
                                                offset=per_page * (pagination.page - 1))


@router_hotels.delete("/{hotel_id}")
async def delete_hotels(db: DBDep, hotel_id: int):
    await db.hotels.delete(hotel_id=hotel_id)
    await db.commit()

    return {'Status': 'Ok'}

@router_hotels.get("/{hotel_id}")
async def get_hotel_one(db: DBDep, hotel_id: int):
    hotel = await db.hotels.get_one_or_none(hotel_id=hotel_id)

    return {'Hotel': hotel}



@router_hotels.post("")
async def create_hotels(db: DBDep, data_hotel: HotelAdd = Body(openapi_examples={
    "1": {
        "summary": "Sochi",
        "value":
            {
                "title": "Sochi",
                "location": "ул. Лазурная дом 1"
            }
    }
})):
    hotel = await db.hotels.add(data_hotel)
    await db.commit()

    return {'Status': 'Ok', 'data': hotel}


@router_hotels.put("/{hotel_id}")
async def update_hotel(db: DBDep, hotel_id: int, data_hotel: HotelAdd):
    await db.hotels.update(data_hotel, id=hotel_id)
    await db.commit()

    return {"Status": "Ok"}


@router_hotels.patch("/{hotel_id}")
async def update_patch_hotel(db: DBDep, hotel_id: int, data_hotel: HotelPATCH):
    await db.hotels.update(data_hotel, exclude_unset=True, id=hotel_id)
    await db.commit()
    return {"Status": "Ok"}
