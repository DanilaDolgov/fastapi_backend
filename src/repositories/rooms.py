from datetime import date
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from src.models.bookings import BookingsOrm
from src.repositories.base import BaseRepository
from src.models.rooms import RoomsOrm
from src.repositories.mapper.mapper import RoomDataMapper
from src.schemas.rooms import RoomWithReal


class RoomsRepository(BaseRepository):
    model = RoomsOrm
    mapper = RoomDataMapper

    async def get_filtered_by_time(self, hotel_id, date_from: date, date_to: date):
        stmt = (
            select(RoomsOrm)
            .options(joinedload(self.model.facilities))
            .join(
                BookingsOrm,
                (BookingsOrm.room_id == RoomsOrm.id)
                & (BookingsOrm.date_to >= date_from)
                & (BookingsOrm.date_from <= date_to),
                isouter=True,
            )
            .where(RoomsOrm.hotel_id == hotel_id)
            .group_by(RoomsOrm.id, RoomsOrm.quantity)
            .having(
                RoomsOrm.quantity - func.coalesce(func.count(BookingsOrm.id), 0) > 0
            )
        )
        result = await self.session.execute(stmt)
        if result:
            return [
                RoomWithReal.model_validate(model, from_attributes=True)
                for model in result.unique().scalars().all()
            ]
        return None

    async def get_one_or_none(self, **filter_by):
        query = (
            select(RoomsOrm)
            .options(joinedload(RoomsOrm.facilities))
            .filter_by(**filter_by)
        )
        result = await self.session.execute(query)
        model = result.unique().scalars().one_or_none()
        if model:
            return RoomWithReal.model_validate(model, from_attributes=True)
        return None
