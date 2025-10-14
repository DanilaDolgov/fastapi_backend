import functools
import json
import asyncio

# from src.connectors.connectors import RedisManager
from src.utils.redis_setting import redis_manager

MAX_RETRIES = 2
RETRY_DELAY = 0.5


def redis_cache(ttl: int = 60):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"{func.__name__}"
            try:
                cached_value = await redis_manager.get(key)
            except Exception as e:
                print(f"⚠️ redis connection {e}")
                for attempt in range(1, MAX_RETRIES + 1):
                    try:
                        await redis_manager.connect()
                        cached_value = await redis_manager.get(key)
                        break
                    except Exception as e:
                        print(f"⚠️ redis connection {e}")
            if cached_value is not None:
                print(f"⚡ Cache hit: {func.__name__}({args}, {kwargs})")
                await redis_manager.close()
                return json.loads(cached_value)

            results = await func(*args, **kwargs)

            try:
                await redis_manager.set(key, json.dumps(results), expire=ttl)
            except Exception as e:
                print(f"⚠️ Failed to cache result: {e}")
                for attempt in range(1, MAX_RETRIES + 1):
                    try:
                        result_schema = [result.model_dump() for result in results]
                        await redis_manager.set(key, json.dumps(result_schema), expire=ttl)
                        print(f"✅ Retry {attempt}: cached successfully")
                        break
                    except Exception as retry_e:
                        print(f"⚠️ Retry {attempt} failed: {retry_e}")
                        if attempt < MAX_RETRIES:
                            await asyncio.sleep(RETRY_DELAY)
                        else:
                            print("❌ All retries failed, giving up on caching.")

            await redis_manager.close()
            return results

        return wrapper

    return decorator
