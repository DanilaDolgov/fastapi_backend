from sqlalchemy import select, func

from src.hotels.models.hotels import HotelsOrm
from src.repositories.base import BaseRepository


class HotelsRepository(BaseRepository):
    model = HotelsOrm

    async def get_all(self, location, title, limit, offset):
        query = select(HotelsOrm)
        if location:
            query = query.filter(func.lower(HotelsOrm.location).like(f'%{location.strip().lower()}%'))
        if title:
            query = query.filter(func.lower(HotelsOrm.title).like(f"%{title.strip().lower()}%"))
        query = (
            query
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)

        return result.scalars().all()
