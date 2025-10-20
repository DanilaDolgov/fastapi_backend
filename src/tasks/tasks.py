import asyncio

from src.config import settings
from src.database import async_session_maker_null_pool
from src.services.telegramm.api import TgClient
from src.tasks.celery_app import celery_instance
from src.utils.db_manager import DBManager
from src.dependencies.dependencies import get_client
from src.services.email_templates import send_checkin_emails


@celery_instance.task
def test_task(a: str):
    print(a)


# ЗАПУСК АСИНХРОННОЙ ЗАДАЧИ В СЕЛЕРИ


async def data_for_email_send():
    # ДОБАВЬ ЛОГИКУ В ЗАДАЧУ
    # async with DBManager(session_factory=async_session_maker_null_pool) as db:
    #     bookings = await db.booking.get_all()
    print("---------------Start TASK---------------------------------")
    async with DBManager(session_factory=async_session_maker_null_pool) as db:
        bookings = await db.booking.user_checkin_room_email()
        s3 = get_client()
        for booking in bookings:
            booking["images"] = await s3.generate_presigned_urls_by_prefix(
                prefix=f"rooms/{booking['room_id']}/"
            )
        await send_checkin_emails(bookings)


@celery_instance.task(name="booking_today_checkin")
def send_email_user_for_booking_today_checkin():
    # ПРИ ВЫЗОВЕ КАЖДЫЙ РАЗ СОЗДАЕТСЯ НОВЫЙ EVENT LOOP
    # ЧТОБЫ РАБОТАЛО НУЖНО СОЗДАТЬ новый pool для одного подключения
    # async_session_maker_null_pool = async_sessionmaker(bind=engine_null_pool, expire_on_commit=False)

    asyncio.run(data_for_email_send())


async def send_massage_about_exception_in_Telegram(ex: str):
    async with DBManager(session_factory=async_session_maker_null_pool) as db:
        chat_ids = await db.telegramm.get_all()
        tg_client = TgClient(token=settings.telegram_token)
        for chat_id in chat_ids:
            await tg_client.send_message(chat_id=chat_id.chat_id, text=ex)

@celery_instance.task(name="send_in_telegram")
def send_in_telegram(ex):
    asyncio.run(send_massage_about_exception_in_Telegram(ex))