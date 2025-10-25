from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
import logging
from loguru import logger
import sys
from pathlib import Path
from prometheus_fastapi_instrumentator import Instrumentator


sys.path.append(str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO)

from src.api.auth import router as router_auth
from src.api.hotels import router_hotels
from src.api.rooms import router_rooms
from src.api.bookings import booking_router as router_booking
from src.api.facilities import router_facilities
from src.rate_many.api.rate import many_router
from src.utils.redis_setting import redis_manager
from src.api.telegram_webhook import webhook_telegram
from src.utils.s3_settings import s3_manager, s3_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_manager.connect()
    await s3_client.init()
    try:
        async with s3_client as client:
            print(f"[DEBUG S3] client id={id(client)}")
            resp = await client.list_buckets()
            print(f"[S3 CONNECTED] Buckets available: {[b['Name'] for b in resp.get('Buckets', [])]}")
    except Exception as e:
        print(f"[S3 CONNECTION ERROR] {type(e).__name__}: {e}")
    FastAPICache.init(RedisBackend(redis_manager._client), prefix="fastapi-cache")
    yield
    await redis_manager.close()
    await s3_client.shutdown()


app = FastAPI(docs_url=None, lifespan=lifespan)


app.include_router(router_auth)
app.include_router(router_hotels)
app.include_router(router_rooms)
app.include_router(router_booking)
app.include_router(router_facilities)
app.include_router(many_router)
app.include_router(webhook_telegram)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.add("logs/app.log", rotation="10 MB", retention="7 days")
instrumentator = Instrumentator().instrument(app)
instrumentator.expose(app)
logger = logging.getLogger("uvicorn.error")


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
    )


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
