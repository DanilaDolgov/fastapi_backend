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


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_manager.connect()
    FastAPICache.init(RedisBackend(redis_manager._client), prefix="fastapi-cache")
    yield
    await redis_manager.close()


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

@app.exception_handler(Exception)
async def all_exception_handler(request: Request, exc: Exception):
    # Логируем ошибки 5XX
    logger.error(f"5XX | Path: {request.url.path} | Error: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

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
