from typing import Annotated

from aiobotocore.client import AioBaseClient
from pydantic import BaseModel
from fastapi import Query, Depends, Request, HTTPException

from src.database import async_session_maker
from src.exceptions import ObjectNotFoundException
from src.schemas.bookings import BookingRequest
from src.schemas.hotels import Hotel
from src.schemas.rooms import Room
from src.services.auth import AuthService
from src.utils.db_manager import DBManager
from src.utils.s3_settings import s3_manager, s3_client


class PaginationParams(BaseModel):
    page: Annotated[int | None, Query(1, ge=1)]
    per_page: Annotated[int | None, Query(None, ge=1, lt=30)]


Pagination = Annotated[PaginationParams, Depends()]


def get_token(request: Request):
    token = request.cookies.get("access_token", None)
    if not token:
        raise HTTPException(status_code=401, detail="Not access token.")
    return token


def get_current_user_id(token: str = Depends(get_token)):
    data = AuthService().encode_token(token)
    return data["user_id"]


UserIdDep = Annotated[int, Depends(get_current_user_id)]


def get_db_manager():
    return DBManager(session_factory=async_session_maker)


async def get_db():
    async with get_db_manager() as db:
        yield db


DBDep = Annotated[DBManager, Depends(get_db)]

def get_client_s3():
    return s3_client

async def get_s3_client():
    async with get_client_s3() as client:
        yield client

S3Dep = Annotated[AioBaseClient, Depends(get_s3_client)]

async def get_room_or_404(db: DBDep, hotel_id: int, room_id: int):
    try:
        return await db.rooms.get_one(id=room_id, hotel_id=hotel_id)
    except ObjectNotFoundException:
        raise HTTPException(status_code=404, detail="Room not found.")

room_not_none = Annotated[Room, Depends(get_room_or_404)]

async def get_hotel_or_404(db: DBDep, hotel_id: int):
    try:
        return await db.hotels.get_one(id=hotel_id)
    except ObjectNotFoundException:
        raise HTTPException(status_code=404, detail="Hotel not found.")

hotel_not_none = Annotated[Hotel, Depends(get_hotel_or_404)]

async def get_room_for_booking(
    db: DBDep,
    data_booking: BookingRequest,
):
    try:
        return await db.rooms.get_one(id=data_booking.room_id)
    except ObjectNotFoundException:
        raise HTTPException(status_code=404, detail="Room not found.")

room_not_none_for_booking = Annotated[Room, Depends(get_room_for_booking)]