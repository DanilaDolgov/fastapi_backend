from datetime import date

from sqlalchemy import select, func

from src.models.bookings import BookingsOrm
from src.models.hotels import HotelsOrm
from src.models.rooms import RoomsOrm
from src.repositories.mapper.mapper import HotelDataMapper
from src.repositories.base import BaseRepository


class HotelsRepository(BaseRepository):
    model = HotelsOrm
    mapper = HotelDataMapper

    async def get_all(self, location, title, limit, offset):
        query = select(HotelsOrm)
        if location:
            query = query.filter(
                func.lower(HotelsOrm.location).like(f"%{location.strip().lower()}%")
            )
        if title:
            query = query.filter(
                func.lower(HotelsOrm.title).like(f"%{title.strip().lower()}%")
            )
        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)

        return [
            self.mapper.map_to_domain_entity(hotel) for hotel in result.scalars().all()
        ]

    async def get_filtered_by_time(
        self, location, title, limit, offset, date_from: date, date_to: date, **kwargs
    ):
        stmt = (
            select(RoomsOrm.hotel_id)
            .join(
                BookingsOrm,
                (BookingsOrm.room_id == RoomsOrm.id)
                & (BookingsOrm.date_to >= date_from)
                & (BookingsOrm.date_from <= date_to),
                isouter=True,
            )
            .group_by(RoomsOrm.id, RoomsOrm.quantity)
            .having(
                RoomsOrm.quantity - func.coalesce(func.count(BookingsOrm.id), 0) > 0
            )
        )
        if location:
            stmt = stmt.filter(
                func.lower(HotelsOrm.location).like(f"%{location.strip().lower()}%")
            )
        if title:
            stmt = stmt.filter(
                func.lower(HotelsOrm.title).like(f"%{title.strip().lower()}%")
            )
        print(stmt)
        stmt = stmt.limit(limit).offset(offset)
        return await self.get_in_params(HotelsOrm.id.in_(stmt.distinct()))
