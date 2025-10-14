import json
from typing import AsyncGenerator
import pytest
import os

# from fastapi_cache import FastAPICache
# from fastapi_cache.backends.inmemory import InMemoryBackend
from httpx import AsyncClient, ASGITransport
from dotenv import load_dotenv
from unittest import mock


mock.patch("fastapi_cache.decorator.cache", lambda *args, **kwargs: lambda f: f).start()
load_dotenv(".env_test")
path_files = os.path.join(os.path.dirname(__file__), "test_data")

from src.config import settings
from src.database import Base, engine_null_pool, async_session_maker_null_pool
from src.dependencies.dependencies import get_db
from src.main import app
from src.models import *  # noqa F403
from src.schemas.hotels import HotelAdd
from src.schemas.rooms import RoomAdd
from src.utils.db_manager import DBManager


@pytest.fixture(scope="session", autouse=True)
async def check_mode():
    assert settings.MODE == "TEST"


async def get_db_not_pool():
    async with DBManager(session_factory=async_session_maker_null_pool) as db:
        yield db


@pytest.fixture(scope="function", autouse=True)
async def db():
    async for db in get_db_not_pool():
        yield db


app.dependency_overrides[get_db] = get_db_not_pool


@pytest.fixture(scope="session", autouse=True)
async def setup_database(check_mode):
    assert settings.MODE == "TEST"

    async with engine_null_pool.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    for file_name in os.listdir(path_files):
        if file_name.endswith(".json"):
            file_path = os.path.join(path_files, file_name)
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "hotels" in file_name:
                    hotels = [HotelAdd(**d) for d in data]
                if "room" in file_name:
                    rooms = [RoomAdd(**d) for d in data]
    async with DBManager(session_factory=async_session_maker_null_pool) as db_:
        await db_.hotels.add_bulk(hotels)
        await db_.rooms.add_bulk(rooms)
        await db_.commit()


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture(scope="session", autouse=True)
async def create_user(ac, setup_database):
    await ac.post(
        url="/auth/register", json={"email": "test@test.com", "password": "1234"}
    )


@pytest.fixture(scope="session", autouse=True)
async def facility(ac, setup_database):
    response = await ac.post("/facilities", json={"title": "SPA"})
    assert response.status_code == 200


# @pytest.fixture(autouse=True, scope="session")
# def init_cache():
#     FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")


@pytest.fixture(scope="session")
async def authenticated_ac(create_user, ac, setup_database):
    response = await ac.post(
        url="/auth/login", json={"email": "test@test.com", "password": "1234"}
    )

    assert "access_token=" in response.headers.get("set-cookie")
    yield ac
