from pydantic import BaseModel, Field
from fastapi import Form

class RoomForm(BaseModel):
    title: str
    description: str | None
    price: int
    quantity: int

def as_form(
        title: str = Form(...),
        description: str = Form(...),
        price: int = Form(...),
        quantity: int = Form(...)
) -> RoomForm:
    return RoomForm(
        title=title,
        description=description,
        price=price,
        quantity=quantity
    )


class RoomAdd(RoomForm):
    hotel_id: int

class Room(RoomAdd):
    id: int

class RoomPatchRequest(BaseModel):
    title: str | None = Field(None)
    description: str | None = Field(None)
    price: int | None = Field(None)
    quantity: int | None = Field(None)

class RoomPATCH(RoomPatchRequest):
    hotel_id: int
