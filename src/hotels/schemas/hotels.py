from pydantic import BaseModel, Field



class Hotel(BaseModel):
    title: str
    name: str
    address: str
    phone: int

class HotelPATCH(BaseModel):
    title: str | None = Field(None)
    name: str | None = Field(None)
    address: str | None = Field(None)
    phone: int | None = Field(None)