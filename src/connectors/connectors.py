import logging
import redis.asyncio as redis
from src.config import settings


class RedisManager:
    def __init__(self, host: str = settings.REDIS_HOST, port: int = settings.REDIS_PORT):
        self.host = host
        self.port = port
        self._client: redis.Redis | None = None

    async def connect(self):
        logging.info(f"Start connect to Redis host={self.host}, port={self.port}")
        if self._client is None:
            self._client = redis.Redis(host=self.host, port=self.port)
        logging.info(f"Successfully connected with Redis host={self.host}, port={self.port}")

    async def set(self, key: str, value: str, expire: int | None = None):
        if self._client is None:
            raise RuntimeError("Redis client is not connected. Call connect() first.")
        await self._client.set(name=key, value=value, ex=expire)

    async def get(self, key: str) -> str | None:
        if self._client is None:
            raise RuntimeError("Redis client is not connected. Call connect() first.")
        value = await self._client.get(name=key)
        return value.decode() if value else None

    async def delete(self, key: str) -> int:
        if self._client is None:
            raise RuntimeError("Redis client is not connected. Call connect() first.")
        return await self._client.delete(key)

    async def close(self):
        if self._client:
            await self._client.close()
            self._client = None
