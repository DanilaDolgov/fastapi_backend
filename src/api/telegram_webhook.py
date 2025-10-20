from fastapi import APIRouter
from src.dependencies.dependencies import DBDep
from src.schemas.telegramm import TelegrammChatBase, TelegramUpdate
from src.config import settings
from src.services.telegramm.api import TgClient
import asyncio

webhook_telegram = APIRouter(prefix="/webhook", tags=["Telegram"])
"""
APIRouter for handling Telegram webhook events.

Prefix: /webhook
Tags: Telegram
"""

@webhook_telegram.post("")
async def telegram_webhook(db: DBDep, update: TelegramUpdate):
    """
    Handle incoming Telegram webhook updates.

    This endpoint processes incoming updates from Telegram. If the message text is '/start',
    it registers the chat in the database and sends a welcome message back to the user.

    Args:
        db (DBDep): Database dependency used to interact with the database.
        update (TelegramUpdate): The incoming Telegram update object.

    Returns:
        dict: A dictionary with the key 'ok' set to True indicating successful handling.
    """
    if update.message:
        chat = update.message.chat
        text = update.message.text

        if text == '/start':
            # Save chat info to the database
            res_schema = TelegrammChatBase(
                chat_id=chat.id,
                first_name=chat.first_name,
                username=chat.username
            )
            await db.telegramm.add(res_schema)
            await db.commit()

            # Send a welcome message to the user
            await TgClient(token=settings.telegram_token).send_message(
                res_schema.chat_id,
                "Привет! Твой chat_id зарегистрирован."
            )

    return {"ok": True}
