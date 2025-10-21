from fastapi import APIRouter, HTTPException
from fastapi.params import Depends

from src.exceptions import AllRoomsAreBookedException, NotCorrectDateException
from src.schemas.bookings import BookingAdd, BookingRequest
from src.dependencies.dependencies import UserIdDep, DBDep, Pagination, \
    room_not_none_for_booking, S3Dep
from src.utils.s3_settings import s3_client

booking_router = APIRouter(prefix="/booking", tags=["Бронирование"])


@booking_router.post("")
async def create_booking(db: DBDep, data_booking: BookingRequest, user_id: UserIdDep, rnn: room_not_none_for_booking):
    if user_id and rnn:
        room = await db.rooms.get_one(id=data_booking.room_id)
        _res = BookingAdd(user_id=user_id, **data_booking.model_dump(), price=room.price)
        try:
            booking = await db.booking.add_booking(_res)
        except (AllRoomsAreBookedException, NotCorrectDateException) as ex:
            raise HTTPException(status_code=409, detail=ex.detail)
        await db.commit()
        return {"Status": "Ok", "data": booking}


@booking_router.get("")
async def get_bookings(db: DBDep, pagination: Pagination):
    per_page = pagination.per_page or 5
    return await db.booking.get_all(limit=per_page, offset=per_page * (pagination.page - 1))


@booking_router.get("/me")
async def get_bookings_me(db: DBDep, user_id: UserIdDep):
    if user_id:
        return await db.booking.get_in_params(user_id=user_id)


@booking_router.get("/users_checkin")
async def get_users_checkin_in_rooms_today(db: DBDep, s3: S3Dep):
    results_bookings = await db.booking.user_checkin_room_email()
    for result_booking in results_bookings:
        result_booking["images"] = await s3_client.generate_presigned_urls_by_prefix(
            client=s3, prefix=f"rooms/{result_booking['room_id']}/"
        )
    return results_bookings
