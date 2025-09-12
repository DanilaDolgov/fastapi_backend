from datetime import date
from sqlalchemy import select, func

from src.models.bookings import BookingsOrm
from src.repositories.base import BaseRepository
from src.models.rooms import RoomsOrm
from src.schemas.rooms import Room


class RoomsRepository(BaseRepository):
    model = RoomsOrm
    schema = Room

    async def get_filtered_by_time(self,
                                   hotel_id,
                                   date_from: date,
                                   date_to: date):
        stmt = (
            select(RoomsOrm.id)
            .join(
                BookingsOrm,
                (BookingsOrm.room_id == RoomsOrm.id)
                & (BookingsOrm.date_to >= date_from)
                & (BookingsOrm.date_from <= date_to),
                isouter=True
            )
            .where(RoomsOrm.hotel_id == hotel_id)
            .group_by(RoomsOrm.id, RoomsOrm.quantity)
            .having(RoomsOrm.quantity - func.coalesce(func.count(BookingsOrm.id), 0) > 0)
        )

        return await self.get_in_params(RoomsOrm.id.in_(stmt))
