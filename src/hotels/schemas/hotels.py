from pydantic import BaseModel, Field



class Hotel(BaseModel):
    title: str
    location: str

class HotelPATCH(BaseModel):
    title: str | None = Field(None)
    location: str | None = Field(None)
    address: str | None = Field(None)
    phone: int | None = Field(None)