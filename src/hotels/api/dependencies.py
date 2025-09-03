from typing import Annotated


from pydantic import BaseModel
from fastapi import Query, Depends, Request, HTTPException

from src.services.auth import AuthService


class PaginationParams(BaseModel):
    page: Annotated[int | None, Query(1, ge=1)]
    per_page: Annotated[int | None, Query(None, ge=1, lt=30)]


PaginationHotels = Annotated[PaginationParams, Depends()]


def get_token(request: Request):
    token = request.cookies.get("access_token", None)
    if not token:
        raise HTTPException(status_code=401, detail="Not access token.")
    return token

def get_current_user_id(token: str = Depends(get_token)):
    data = AuthService().decode_token(token)
    return data["user_id"]



UserIdDep = Annotated[int, Depends(get_current_user_id)]

PaginationRooms = Annotated[PaginationParams, Depends()]