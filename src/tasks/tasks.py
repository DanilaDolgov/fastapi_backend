import asyncio
from src.config import settings
from src.database import async_session_maker_null_pool
from src.telegramm.api import TgClient
from src.tasks.celery_app import celery_instance
from src.utils.db_manager import DBManager
from src.utils.s3_client import S3Client
from src.utils.s3_manager import S3Manager
from src.utils.email_templates import send_checkin_emails



def run_async_task(async_func, *args, **kwargs):
    """Безопасно запускает любую асинхронную функцию внутри Celery-таски."""
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(async_func(*args, **kwargs))
    finally:
        loop.close()



async def init_s3() -> S3Manager:
    """Создаёт и инициализирует S3Manager с новым S3Client."""
    s3_client = S3Client()
    await s3_client.init()
    return S3Manager(s3_client=s3_client)



async def data_for_email_send(s3_manager: S3Manager):
    print("---------------Start TASK---------------------------------")

    async with DBManager(session_factory=async_session_maker_null_pool) as db:
        bookings = await db.booking.user_checkin_room_email()

        for booking in bookings:
            booking["images"] = await s3_manager.generate_presigned_urls_by_prefix(
                prefix=f"rooms/{booking['room_id']}/"
            )

    await send_checkin_emails(bookings)

    await s3_manager._s3_client.shutdown()



@celery_instance.task(name="booking_today_checkin")
def send_email_user_for_booking_today_checkin():
    """Celery-таска, изолированно запускающая async email рассылку."""
    async def task_logic():
        s3_manager = await init_s3()
        await data_for_email_send(s3_manager)

    run_async_task(task_logic)



async def send_message_about_exception_in_telegram(ex: str):
    async with DBManager(session_factory=async_session_maker_null_pool) as db:
        chat_ids = await db.telegramm.get_all()

    tg_client = TgClient(token=settings.telegram_token)
    for chat_id in chat_ids:
        await tg_client.send_message(chat_id=chat_id.chat_id, text=ex)


@celery_instance.task(name="send_in_telegram")
def send_in_telegram(ex: str):
    run_async_task(send_message_about_exception_in_telegram, ex)

