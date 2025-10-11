from datetime import date

from src.schemas.bookings import BookingAdd

async def test_create_booking(db):
    user_id = (await db.user.get_all())[0].id
    room_id = (await db.rooms.get_all())[0].id
    data = BookingAdd(user_id=user_id,
                      room_id=room_id,
                      date_from=date(year=2025, month=10, day=13),
                      date_to=date(year=2025, month=10, day=15),
                      price=4500)
    booking = await db.booking.add(data)

    assert await db.booking.get_in_params(id=booking.id)

    booking.room_id = (await db.rooms.get_all())[1].id
    await db.booking.update(booking)
    booking = (await db.booking.get_in_params(id=booking.id))[0]
    assert room_id != booking.room_id

    booking_id = booking.id
    await db.booking.delete(id=booking.id)
    booking = db.booking.get_one_or_none(id=booking_id)
    assert booking is not None

    await db.commit()