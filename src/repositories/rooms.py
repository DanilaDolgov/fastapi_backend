from datetime import date


from pydantic_core._pydantic_core import ValidationError
from sqlalchemy import select, func, delete
from sqlalchemy.orm import joinedload

from src.exceptions import HotelOrRoomsNotFoundException, NotCorrectDateException
from src.models.bookings import BookingsOrm
from src.repositories.base import BaseRepository
from src.models.rooms import RoomsOrm
from src.repositories.mapper.mapper import RoomDataMapper
from src.schemas.rooms import RoomWithReal
from src.models.facilities import FacilitiesRoomsOrm


class RoomsRepository(BaseRepository):
    model = RoomsOrm
    mapper = RoomDataMapper

    async def get_filtered_by_time(self, hotel_id, date_from: date, date_to: date):
        if date_to == date_from or date_to < date_from:
            raise NotCorrectDateException
        stmt = (
            select(RoomsOrm)
            .options(joinedload(self.model.facilities))
            .join(
                BookingsOrm,
                (BookingsOrm.room_id == RoomsOrm.id)
                & (BookingsOrm.date_to > date_from)
                & (BookingsOrm.date_from < date_to),
                isouter=True,
            )
            .where(RoomsOrm.hotel_id == hotel_id)
            .group_by(RoomsOrm.id, RoomsOrm.quantity)
            .having(RoomsOrm.quantity - func.coalesce(func.count(BookingsOrm.id), 0) > 0)
        )
        result = await self.session.execute(stmt)
        return [
            self.mapper.map_to_domain_entity(model)
            for model in result.unique().scalars().all()
        ]


    async def delete_rooms(self, room_id, hotel_id):
        delete_stmt_f = delete(FacilitiesRoomsOrm).filter_by(rooms_id=room_id)
        await self.session.execute(delete_stmt_f)
        delete_stmt_r = delete(RoomsOrm).filter_by(id=room_id, hotel_id=hotel_id)
        await self.session.execute(delete_stmt_r)
    


