from typing import Annotated
from pydantic import BaseModel
from fastapi import Query, Depends



class PaginationParams(BaseModel):
    page: Annotated[int | None, Query(1, ge=1)]
    per_page: Annotated[int | None, Query(None, ge=1, lt=30)]


PaginationHotels = Annotated[PaginationParams, Depends()]