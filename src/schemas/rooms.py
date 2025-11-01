from pydantic import Field, ConfigDict, BaseModel, field_validator
from typing import List, Optional

from src.schemas.facilities import Facilities


class RoomAddRequest(BaseModel):
    title: str
    description: Optional[str] = None
    price: int
    quantity: int
    facilities_ids: Optional[List[int]] = None

    @field_validator("title", mode="before")
    def validate_title(cls, v: str):
        v = v.strip()
        if not v:
            raise ValueError("Название номера не может быть пустым или состоять из пробелов.")
        if len(v) < 5:
            raise ValueError("Название номера должно содержать минимум 5 символов.")
        return v

    @field_validator("price", mode="before")
    def validate_price(cls, v: int):
        if v <= 0:
            raise ValueError("Цена не может быть меньше или равно нулю.")
        return v

    @field_validator("quantity", mode="before")
    def validate_quantity(cls, v: int):
        if v <= 0:
            raise ValueError("Количество номеров не может быть меньше или равно нуля.")
        return v


class RoomAdd(BaseModel):
    hotel_id: int
    title: str
    description: str | None = None
    price: int
    quantity: int




class Room(RoomAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)


class RoomWithReal(Room):
    facilities: list[Facilities]

    model_config = ConfigDict(from_attributes=True)


class RoomPatchRequest(BaseModel):
    title: str | None = Field(None)
    description: str | None = Field(None)
    price: int | None = Field(None)
    quantity: int | None = Field(None)
    facilities_ids: Optional[List[int]] = None

    @field_validator("title", mode="before")
    def validate_title(cls, v: str):
        v = v.strip()
        if not v:
            raise ValueError("Название номера не может быть пустым или состоять из пробелов.")
        if len(v) < 5:
            raise ValueError("Название номера должно содержать минимум 5 символов.")
        return v

    @field_validator("price", mode="before")
    def validate_price(cls, v: int):
        if v <= 0:
            raise ValueError("Цена не может быть меньше или равна нулю.")
        return v

    @field_validator("quantity", mode="before")
    def validate_quantity(cls, v: int):
        if v <= 0:
            raise ValueError("Количество номеров не может быть меньше или равна нулю.")
        return v




class RoomPATCH(BaseModel):
    hotel_id: int
    title: str | None = Field(None)
    description: str | None = Field(None)
    price: int | None = Field(None)
    quantity: int | None = Field(None)

    @field_validator("title", mode="before")
    def validate_title(cls, v: str):
        v = v.strip()
        if not v:
            raise ValueError("Название номера не может быть пустым или состоять из пробелов.")
        if len(v) < 5:
            raise ValueError("Название номера должно содержать минимум 5 символов.")
        return v

    @field_validator("price", mode="before")
    def validate_price(cls, v: int):
        if v <= 0:
            raise ValueError("Цена не может быть меньше или равна нулю.")
        return v

    @field_validator("quantity", mode="before")
    def validate_quantity(cls, v: int):
        if v <= 0:
            raise ValueError("Количество номеров не может быть меньше или равна нулю.")
        return v


