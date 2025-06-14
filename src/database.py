from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy import text
import asyncio

from src.config import settings


engine = create_async_engine(f"{settings.DB_URL}")


