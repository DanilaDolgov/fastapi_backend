from src.repositories.base import BaseRepository
from src.bookings.models.bookings import BookingsOrm
from src.bookings.schemas.bookings import Booking


class BookingsRepository(BaseRepository):
    model = BookingsOrm
    schema = Booking

