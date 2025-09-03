from pydantic import BaseModel, Field


class RoomShow(BaseModel):
    title: str
    description: str | None
    price: int
    quantity: int


class RoomAdd(RoomShow):
    hotel_id: int

class Room(RoomAdd):
    id: int

class RoomPATCH(BaseModel):
    title: str | None = Field(None)
    description: str | None = Field(None)
    price: int | None = Field(None)
    quantity: int | None = Field(None)

