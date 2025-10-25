import pytest

from src.config import settings
from src.database import engine_null_pool, Base

@pytest.fixture(scope="session", autouse=True)
async def booking_add(authenticated_ac):
    response = await authenticated_ac.post(
        "/booking",
        json={"room_id": 5, "date_from": "2025-10-13", "date_to": "2025-10-20"})

@pytest.mark.parametrize("date_from, date_to",[
    ("2025-10-13", "2025-10-20"),
    ("2025-10-20", "2025-10-13"),
],)
async def test_get_hotels(ac, date_from, date_to):
    response = await ac.get(
        "/hotels",
        params={
            "date_from": date_from,
            "date_to": date_to,
        },
    )
    if response.status_code == 200:
        assert response.status_code == 200
        assert len(response.json()["data"]) == 3
    else:
        assert response.status_code == 400