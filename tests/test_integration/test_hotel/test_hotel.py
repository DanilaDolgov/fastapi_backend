from src.schemas.hotels import HotelAdd


async def test_create_hotel(db):
    data = HotelAdd(title='Sochi five stars', location='Sochi, str. Revolucii, 5')
    hotel = await db.hotels.add(data)
    print(hotel)
    await db.commit()