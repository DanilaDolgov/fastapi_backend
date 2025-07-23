from pydantic import BaseModel, Field



class HotelAdd(BaseModel):
    title: str
    location: str

class Hotel(HotelAdd):
    id: int

class HotelPATCH(BaseModel):
    title: str | None = Field(None)
    location: str | None = Field(None)
    address: str | None = Field(None)
    phone: int | None = Field(None)