from pydantic import BaseModel, Field
from fastapi import Form
from datetime import date


class BookingAdd(BaseModel):
    date_from: date
    date_to: date

class Booking(BookingAdd):
    user_id: int
    room_id: int
    price: int

