from datetime import date
import pytest

from src.config import settings
from src.database import engine_null_pool, Base
from src.models import BookingsOrm


@pytest.mark.parametrize(
    "room_id, date_from, date_to",
    [
        (1, "2025-10-21", "2025-10-22"),
        (1, "2025-10-21", "2025-10-22"),
        (1, "2025-10-21", "2025-10-22"),
        (1, "2025-10-21", "2025-10-22"),
        (1, "2025-10-21", "2025-10-22"),
        (1, "2025-10-21", "2025-10-22"),
        (1, "2025-10-22", "2025-10-23"),
    ],
)
async def test_booking_add(room_id, date_from, date_to, db, authenticated_ac):
    response = await authenticated_ac.post(
        "/booking",
        json={"room_id": room_id, "date_from": date_from, "date_to": date_to},
    )
    if response.status_code == 200:
        assert response.json()["Status"] == "Ok"
        assert response.json()["data"]
        assert isinstance(response.json(), dict)
        from_date = date.fromisoformat(date_from)
        to_date = date.fromisoformat(date_to)
        assert (
            len(
                await db.booking.get_in_params(
                    room_id=room_id, date_from=from_date, date_to=to_date
                )
            )
            <= 5
        )
    else:
        from_date = date.fromisoformat(date_from)
        to_date = date.fromisoformat(date_to)
        assert (
            len(
                await db.booking.get_in_params(
                    room_id=room_id, date_from=from_date, date_to=to_date
                )
            )
            == 5
        )


@pytest.fixture(scope="session")
async def delete_and_create_table_booking():
    assert settings.MODE == "TEST"

    async with engine_null_pool.begin() as conn:
        await conn.run_sync(
            lambda sync_conn: Base.metadata.drop_all(
                sync_conn, tables=[BookingsOrm.__table__], checkfirst=True
            )
        )
        await conn.run_sync(
            lambda sync_conn: Base.metadata.create_all(
                sync_conn, tables=[BookingsOrm.__table__], checkfirst=True
            )
        )


@pytest.mark.parametrize(
    "room_id, date_from, date_to, count_bookings_for_user",
    [
        (1, "2025-10-21", "2025-10-22", 1),
        (1, "2025-10-21", "2025-10-22", 2),
        (1, "2025-10-21", "2025-10-22", 3),
        (1, "2025-10-21", "2025-10-22", 4),
        (1, "2025-10-21", "2025-10-22", 5),
        (1, "2025-10-21", "2025-10-22", 5),
        (1, "2025-10-22", "2025-10-23", 6),
    ],
)
async def test_add_and_get_bookings(
    room_id,
    date_from,
    date_to,
    count_bookings_for_user,
    delete_and_create_table_booking,
    authenticated_ac,
):
    res_test = await authenticated_ac.get("/booking/me")
    if not res_test.json():
        print("Таблица Booking пуста!")
    await authenticated_ac.post(
        "/booking",
        json={"room_id": room_id, "date_from": date_from, "date_to": date_to},
    )
    response_booking_me = await authenticated_ac.get("/booking/me")
    assert len(response_booking_me.json()) == count_bookings_for_user
