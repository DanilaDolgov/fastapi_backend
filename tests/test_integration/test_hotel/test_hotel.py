from src.database import async_session_maker, async_session_maker_null_pool
from src.schemas.hotels import HotelAdd
from src.utils.db_manager import DBManager


async def test_create_hotel():
    data = HotelAdd(title='Sochi five stars', location='Sochi, str. Revolucii, 5')
    async with DBManager(session_factory=async_session_maker_null_pool) as db:
        hotel = await db.hotels.add(data)
        print(hotel)
        await db.commit()