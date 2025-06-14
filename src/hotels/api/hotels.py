from fastapi import Query, APIRouter

from src.hotels.api.dependencies import PaginationHotels
from src.hotels.schemas.hotels import Hotel, HotelPATCH

router_hotels = APIRouter(prefix="/hotels", tags=["Отели"])

hotels = [
    {"id": 1, "title": "Sochi", "name": "Sochi", "address": "RUSSIA, KRASNODARSKII KRAI, SOCHI", "phone": 7999999999},
    {"id": 2, "title": "Дубай", "name": "Дубай", "address": "UAE, DUBAI", "phone": 97100000000},
    {"id": 3, "title": "Krasnodar", "name": "Krasnodar", "address": "Russia, Krasnodar", "phone": 711111111111},
    {"id": 4, "title": "Kaliningrad", "name": "Kaliningrad", "address": "Russia, Kaliningrad", "phone": 722222222},
    {"id": 5, "title": "Tver", "name": "Tver", "address": "Russia, Tver", "phone": 73333333333},
    {"id": 6, "title": "Kursk", "name": "Kursk", "address": "Russia, Kursk", "phone": 7444444444},
    {"id": 7, "title": "Rostov-na_dony", "name": "Rostov-na_dony", "address": "Russia, Rostov-na_dony", "phone": 75555555555},
    {"id": 8, "title": "Klin", "name": "Klin", "address": "Russia, Klin", "phone": 766666666666},
]


@router_hotels.get("/")
def func():
    return "Hello World!!!!!!!!!!"


@router_hotels.get("")
def get_hotels(
        pagination: PaginationHotels,
        id: int | None = Query(None, description="Айдишник"),
        title: str | None = Query(None, description="Название отеля"),
):
    hotels_ = []
    for hotel in hotels:
        if id and hotel["id"] != id:
            continue
        if title and hotel["title"] != title:
            continue
        hotels_.append(hotel)
    if pagination.page is None and pagination.pre_page is None:
        return hotels_[0:3]
    else:
        return hotels_[pagination.pre_page*(pagination.page-1):][:pagination.pre_page]


@router_hotels.delete("/{hotel_id}")
def delete_hotels(hotel_id: int):
    global hotels
    hotels = [hotel for hotel in hotels if hotel["id"] != hotel_id]
    return {'Status': 'Ok'}


@router_hotels.post("")
def create_hotels(data_hotel: Hotel):
    global hotels
    hotels.append(
        {
            "id": hotels[-1]["id"] + 1,
            "title": data_hotel.title,
            "name": data_hotel.name,
            "address": data_hotel.address,
            "phone": data_hotel.phone
        }
    )
    return {'Status': 'Ok'}


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
