from typing import Annotated


from pydantic import BaseModel
from fastapi import Query, Depends, Request, HTTPException

from src.database import async_session_maker
from src.exceptions import ObjectNotFoundException
from src.services.auth import AuthService
from src.services.s3 import S3Client
from src.utils.db_manager import DBManager


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


def get_client():
    return S3Client()


S3Dep = Annotated[S3Client, Depends(get_client)]

async def get_room_or_404(db: DBDep, hotel_id: int, room_id: int):
    try:
        return await db.rooms.get_one(id=room_id, hotel_id=hotel_id)
    except ObjectNotFoundException:
        raise HTTPException(status_code=404, detail="Room not found.")

room_not_none = Annotated[ObjectNotFoundException, Depends(get_room_or_404)]

async def get_hotel_or_404(db: DBDep, hotel_id: int):
    try:
        return await db.hotels.get_one(id=hotel_id)
    except ObjectNotFoundException:
        raise HTTPException(status_code=404, detail="Hotel not found.")

hotel_not_none = Annotated[ObjectNotFoundException, Depends(get_hotel_or_404)]