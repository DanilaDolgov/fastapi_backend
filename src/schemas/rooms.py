from pydantic import BaseModel, Field, ConfigDict, ValidationError
from typing import Optional, List, Annotated
from fastapi import Form, Depends
import json




import json
from fastapi import Form, File, UploadFile, Depends
from pydantic import BaseModel
from typing import List, Optional

from src.schemas.facilities import Facilities


class RoomAddRequest(BaseModel):
    title: str
    description: Optional[str] = None
    price: int
    quantity: int
    facilities_ids: Optional[List[int]] = None



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

class RoomPatchRequest(BaseModel):
    title: str | None = Field(None)
    description: str | None = Field(None)
    price: int | None = Field(None)
    quantity: int | None = Field(None)
    facilities_ids: Optional[List[int]] = None

class RoomPATCH(BaseModel):
    hotel_id: int
    title: str | None = Field(None)
    description: str | None = Field(None)
    price: int | None = Field(None)
    quantity: int | None = Field(None)

    # model_config = ConfigDict(from_attributes=True)
