import json

import asyncio
import pytest
import os
from httpx import AsyncClient, ASGITransport

from src.config import settings
from src.database import Base, engine_null_pool, async_session_maker_null_pool
from src.main import app
from src.models import *

from dotenv import load_dotenv

from src.schemas.hotels import HotelAdd
from src.schemas.rooms import RoomAdd
from src.utils.db_manager import DBManager

load_dotenv(".env_test")
path_files = os.path.join(os.path.dirname(__file__), "test_data")

@pytest.fixture(scope="session", autouse=True)
async def check_mode():
    assert settings.MODE == "TEST"
    print(settings.MODE)
    print(os.listdir(path_files))
    for file_name in os.listdir(path_files):
        print(path_files + file_name)

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
                data = json.load(f)  # загружаем весь JSON целиком
                if 'hotels' in file_name:
                    hotel = [HotelAdd(**d) for d in data]
                    async with DBManager(session_factory=async_session_maker_null_pool) as db:
                        hotel = await db.hotels.add_bulk(hotel)
                        await db.commit()
                if 'room' in file_name:
                    rooms = [RoomAdd(**d) for d in data]
                    async with DBManager(session_factory=async_session_maker_null_pool) as db:
                        room = await db.rooms.add_bulk(rooms)
                        await db.commit()


@pytest.fixture(scope="session", autouse=True)
async def create_user(setup_database):
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        await ac.post(url="/auth/register",
                      json={
                          "email": "test@test.com",
                          "password": "1234"
                      })