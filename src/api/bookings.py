from typing import Dict

from fastapi import APIRouter

from src.schemas.bookings import BookingAdd, Booking, BookingRequest
from src.dependencies.dependencies import UserIdDep, DBDep, Pagination, S3Dep

booking_router = APIRouter(prefix="/booking", tags=["Бронирование"])


@booking_router.post("")
async def create_booking(db: DBDep, data_booking: BookingRequest, user_id: UserIdDep):
    if user_id:
        room = await db.rooms.get_one_or_none(id=data_booking.room_id)
        _res = BookingAdd(user_id=user_id, **data_booking.model_dump(), price=room.price)
        booking = await db.booking.add_booking(_res)
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

@booking_router.get("/users_checkin")
async def get_users_checkin_in_rooms_today(db: DBDep, s3: S3Dep):
    results_bookings = await db.booking.user_checkin_room_email()
    for result_booking in results_bookings:
        result_booking["images"] = await s3.generate_presigned_urls_by_prefix(prefix=f'rooms/{result_booking["room_id"]}/')
    return results_bookings






