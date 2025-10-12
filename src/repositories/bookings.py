from datetime import datetime, date
from fastapi import HTTPException
from sqlalchemy import select, func

from src.models.facilities import FacilitiesOrm, FacilitiesRoomsOrm
from src.models.hotels import HotelsOrm
from src.models.rooms import RoomsOrm
from src.models.users import UsersOrm
from src.repositories.base import BaseRepository
from src.models.bookings import BookingsOrm
from src.repositories.mapper.mapper import BookingDataMapper
from src.schemas.bookings import Booking, BookingAdd


class BookingsRepository(BaseRepository):
    model = BookingsOrm
    mapper = BookingDataMapper

    async def user_checkin_room_email(self) -> list[dict]:
        query = (
            select(
                BookingsOrm.date_to,
                BookingsOrm.date_from,
                BookingsOrm.price,
                UsersOrm.email,
                RoomsOrm.id.label("room_id"),
                RoomsOrm.title.label("room_title"),
                RoomsOrm.description.label("room_description"),
                HotelsOrm.title.label("hotel_title"),
                HotelsOrm.location.label("hotel_location"),
                func.array_agg(FacilitiesOrm.title).label("facilities_name"),
            )
            .join(RoomsOrm, BookingsOrm.room_id == RoomsOrm.id)
            .join(UsersOrm, UsersOrm.id == BookingsOrm.user_id)
            .join(HotelsOrm, RoomsOrm.hotel_id == HotelsOrm.id)
            .join(FacilitiesRoomsOrm, RoomsOrm.id == FacilitiesRoomsOrm.rooms_id)
            .join(FacilitiesOrm, FacilitiesRoomsOrm.facilities_id == FacilitiesOrm.id)
            .where(BookingsOrm.date_from == datetime.now().date())
            .group_by(
                BookingsOrm.id,
                UsersOrm.email,
                RoomsOrm.id,
                RoomsOrm.title,
                RoomsOrm.description,
                HotelsOrm.title,
                HotelsOrm.location,
                BookingsOrm.date_to,
                BookingsOrm.date_from,
                BookingsOrm.price,
            )
        )

        result = await self.session.execute(query)

        bookings = [
            dict(
                date_to=row.date_to,
                date_from=row.date_from,
                price=row.price * (row.date_to - row.date_from).days,
                email=row.email,
                room_id=row.room_id,
                room_title=row.room_title,
                room_description=row.room_description,
                hotel_title=row.hotel_title,
                hotel_location=row.hotel_location,
                facilities_name=row.facilities_name,
            )
            for row in result
        ]

        return bookings

    async def add_booking(self, model: BookingAdd):
        stmt = (
                select(RoomsOrm)
                .join(
                    BookingsOrm,
                    (BookingsOrm.room_id == RoomsOrm.id)
                    & (BookingsOrm.date_to >= model.date_from)
                    & (BookingsOrm.date_from <= model.date_to),
                    isouter=True
                )
                .where(RoomsOrm.id == model.room_id)
                .group_by(RoomsOrm.id, RoomsOrm.quantity)
                .having(RoomsOrm.quantity - func.coalesce(func.count(BookingsOrm.id), 0) > 0)
            )
        result = await self.session.execute(stmt)
        rooms = result.scalars().all()
        from src.dependencies.dependencies import get_db_manager
        if rooms:
            async with get_db_manager() as db:
                booking = await db.booking.add(model)
                await db.commit()
                return  booking

        else:
            raise HTTPException(
                status_code=400,
                detail="Нет свободных номеров на выбранные даты"
            )


