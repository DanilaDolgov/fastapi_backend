from fastapi import Query, APIRouter, Body
from sqlalchemy import insert, select, func

from src.database import async_session_maker
from src.hotels.api.dependencies import PaginationHotels
from src.hotels.models.hotels import HotelsOrm
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

    #     return hotels
    # if pagination.page is None and pagination.pre_page is None:
    #     return hotels[0:3]
    # else:
    #     return hotels[pagination.pre_page * (pagination.page - 1):][:pagination.pre_page]


@router_hotels.delete("/{hotel_id}")
def delete_hotels(hotel_id: int):
    global hotels
    hotels = [hotel for hotel in hotels if hotel["id"] != hotel_id]
    return {'Status': 'Ok'}


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
def update_hotel(hotel_id: int, data_hotel: Hotel):
    global hotels
    hotels = [{**hotel, "title": data_hotel.title, "name": data_hotel.name, "address": data_hotel.address,
               "phone": data_hotel.phone} if
              hotel["id"] == hotel_id else hotel for hotel in hotels]
    return {"Status": "Ok"}


@router_hotels.patch("/{hotel_id}")
def update_patch_hotel(hotel_id: int, data_hotel: HotelPATCH):
    global hotels
    hotels = [
        {
            **hotel,
            "title": data_hotel.title if data_hotel.title is not None else hotel["title"],
            "name": data_hotel.name if data_hotel.name is not None else hotel["name"],
            "address": data_hotel.address if data_hotel.address is not None else hotel["address"],
            "phone": data_hotel.phone if data_hotel.phone is not None else hotel["phone"]
        } if hotel["id"] == hotel_id else hotel
        for hotel in hotels
    ]
    return {"Status": "Ok"}
