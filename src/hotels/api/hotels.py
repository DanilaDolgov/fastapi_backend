from fastapi import Query, APIRouter, Body
from src.database import async_session_maker
from src.hotels.api.dependencies import PaginationHotels
from src.hotels.schemas.hotels import Hotel, HotelPATCH
from src.repositories.hotels import HotelsRepository

router_hotels = APIRouter(prefix="/hotels", tags=["Отели"])





@router_hotels.get("")
async def get_hotels(
        pagination: PaginationHotels,
        title: str | None = Query(None, description="Название отеля"),
        location: str | None = Query(None, description="Адрес отеля")
):
    per_page = pagination.per_page or 5
    async with async_session_maker() as session:
       return await HotelsRepository(session=session).get_all(
            location=location,
            title=title,
            limit=per_page,
            offset=per_page * (pagination.page - 1))


@router_hotels.delete("/{hotel_id}")
async def delete_hotels(hotel_id: int):
    async with async_session_maker() as session:
        await HotelsRepository(session).delete(id=hotel_id)
        await session.commit()

    return {'Status': 'Ok'}

@router_hotels.get("/{hotel_id}")
async def get_hotel_one(hotel_id: int):
    async with async_session_maker() as session:
        hotel = await HotelsRepository(session).get_one(id=hotel_id)
        await session.commit()
    return {'Hotel': hotel}



@router_hotels.post("")
async def create_hotels(data_hotel: Hotel = Body(openapi_examples={
    "1": {
        "summary": "Sochi",
        "value":
            {
                "title": "Sochi",
                "location": "ул. Лазурная дом 1"
            }
    }
})):

    async with async_session_maker() as session:
        hotel = await HotelsRepository(session).add(data_hotel)
        await session.commit()
    return {'Status': 'Ok', 'data': hotel}


@router_hotels.put("/{hotel_id}")
async def update_hotel(hotel_id: int, data_hotel: Hotel):

    async with async_session_maker() as session:
        await HotelsRepository(session).update(data_hotel, id=hotel_id)
        await session.commit()
    return {"Status": "Ok"}


@router_hotels.patch("/{hotel_id}")
async def update_patch_hotel(hotel_id: int, data_hotel: HotelPATCH):

    async with async_session_maker() as session:
        await HotelsRepository(session).update(data_hotel, exclude_unset=True, id=hotel_id)
        await session.commit()

    return {"Status": "Ok"}
