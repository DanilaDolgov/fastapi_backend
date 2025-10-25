from datetime import date
from fastapi import Query, HTTPException

from src.dependencies.dependencies import Pagination
from src.exceptions import NotCorrectDateException
from src.schemas.hotels import HotelAdd
from src.services.base import BaseServices


class HotelServices(BaseServices):
    async def get_filtered_by_time(self,
            pagination: Pagination,
            date_to: date,
            date_from: date,
            title: str | None = Query(None, description="Название отеля"),
            location: str | None = Query(None, description="Адрес отеля"),
    ):
        per_page = pagination.per_page or 5
        return await self.db.hotels.get_filtered_by_time(
            date_from=date_from,
            date_to=date_to,
            title=title,
            location=location,
            limit=per_page,
            offset=per_page * (pagination.page - 1),
        )

    async def get_one(self, hotel_id: int):
        hotel = await self.db.hotels.get_one(id=hotel_id)
        return hotel

    async def add_hotel(self, data_hotel: HotelAdd):
        hotel = await self.db.hotels.add(data_hotel)
        await self.db.commit()

        return hotel

    async def delete_hotels(self, hotel_id):
        await self.db.hotels.delete(id=hotel_id)
        await self.db.commit()

    async def update_hotel(self, hotel_id, data_hotel: HotelAdd):
        await self.db.hotels.update(data_hotel, id=hotel_id)
        await self.db.commit()

    async def update_patch_hotel(self, data_hotel, hotel_id):
        await self.db.hotels.update(data_hotel, exclude_unset=True, id=hotel_id)
        await self.db.commit()
