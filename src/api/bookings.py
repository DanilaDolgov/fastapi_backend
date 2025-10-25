from fastapi import APIRouter, HTTPException
from fastapi.params import Depends

from src.exceptions import AllRoomsAreBookedException, NotCorrectDateException
from src.schemas.bookings import BookingAdd, BookingRequest
from src.dependencies.dependencies import UserIdDep, DBDep, Pagination, \
    room_not_none_for_booking, S3Dep
from src.services.bookings import BookingServices
from src.utils.s3_settings import s3_manager

booking_router = APIRouter(prefix="/booking", tags=["Бронирование"])


@booking_router.post("")
async def create_booking(db: DBDep, data_booking: BookingRequest, user_id: UserIdDep, rnn: room_not_none_for_booking):
    if user_id and rnn:
        try:
            booking = await BookingServices(db).create_booking(data_booking=data_booking, user_id=user_id)
        except (AllRoomsAreBookedException, NotCorrectDateException) as ex:
            raise HTTPException(status_code=409, detail=ex.detail)
        return {"Status": "Ok", "data": booking}


@booking_router.get("")
async def get_bookings(db: DBDep, pagination: Pagination):
    bookings = await BookingServices(db).get_bookings(pagination=pagination)
    return bookings


@booking_router.get("/me")
async def get_bookings_me(db: DBDep, user_id: UserIdDep):
    if user_id:
        booking = await BookingServices(db).get_booking_for_me(user_id=user_id)
        return booking



@booking_router.get("/users_checkin")
async def get_bookings_users_checkin_in_rooms_today(db: DBDep):
    result = await BookingServices(db=db, s3=s3_manager).get_users_checkin_in_rooms_today()
    return result
