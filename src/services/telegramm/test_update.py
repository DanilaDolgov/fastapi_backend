import asyncio
import aiohttp
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.config import settings
from src.services.telegramm.api import TgClient

WEBHOOK_URL = "http://127.0.0.1:8000/webhook"

async def update_telegram(tg: TgClient):
    offset = 0
    async with aiohttp.ClientSession() as session:
        while True:
            updates: dict = await tg._perform_request('get', tg.get_path(f'getUpdates?offset={offset}'))
            for upd in updates.get('result', []):
                print(upd)
                offset = upd['update_id'] + 1
                try:
                    resp = await session.post(WEBHOOK_URL, json=upd)
                    print(f"➡️ Sent update {upd['update_id']} ({resp.status})")
                except Exception as e:
                    print(f"❌ Error sending to webhook: {e}")

            await asyncio.sleep(2)

async def main():
    tg = TgClient(token=settings.telegram_token)  # создаем после запуска цикла
    asyncio.create_task(update_telegram(tg))
    while True:
        await asyncio.sleep(3600)

if __name__ == '__main__':
    print("Start")
    asyncio.run(main())
