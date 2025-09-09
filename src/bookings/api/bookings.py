from fastapi import APIRouter

from src.schemas.bookings import BookingAdd, Booking, BookingRequest
from src.dependencies.dependencies import UserIdDep, DBDep, Pagination

booking_router = APIRouter(prefix="/booking", tags=["Бронирование"])


@booking_router.post("")
async def create_booking(db: DBDep, data_booking: BookingRequest, user_id: UserIdDep):
    if user_id:
        room = await db.rooms.get_one_or_none(id=data_booking.room_id)
        _res = BookingAdd(user_id=user_id, **data_booking.model_dump(), price=room.price)
        booking = await db.booking.add(_res)
        await db.commit()

        return {'Status': 'Ok', 'data': booking}

@booking_router.get("")
async def get_bookings(db: DBDep, pagination: Pagination):
    per_page = pagination.per_page or 5
    return await db.booking.get_all(limit=per_page,
                                    offset=per_page * (pagination.page - 1))

@booking_router.get("/me")
async def get_bookings(db: DBDep, user_id: UserIdDep):
    if user_id:
        return await db.booking.get_in_params(user_id=user_id)





