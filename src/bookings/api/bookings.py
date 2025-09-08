from fastapi import Query, APIRouter, Body
from datetime import date

from src.bookings.schemas.bookings import BookingAdd, Booking
from src.hotels.api.dependencies import UserIdDep
from src.database import async_session_maker
from src.hotels.api.dependencies import PaginationHotels, DBDep
from src.hotels.schemas.hotels import Hotel, HotelPATCH, HotelAdd
from src.repositories.bookings import BookingsRepository
from src.repositories.hotels import HotelsRepository
from src.repositories.rooms import RoomsRepository


booking_router = APIRouter(prefix="/booking", tags=["Бронирование"])


@booking_router.post("/{room_id}")
async def create_booking(data_booking: BookingAdd, room_id: int, user_id: UserIdDep):
    if user_id:
        async with async_session_maker() as session:
            room = await RoomsRepository(session).get_one_or_none(id=room_id)
            _res = Booking(user_id=user_id, room_id=room.id, **data_booking.model_dump(), price=room.price)
            booking = await BookingsRepository(session).add(_res)
            await session.commit()
            return {'Status': 'Ok', 'data': booking}




