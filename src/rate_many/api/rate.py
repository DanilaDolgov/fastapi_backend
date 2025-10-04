from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
import requests, asyncio, os

many_router = APIRouter(prefix='/many', tags=["Курс доллара"])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(BASE_DIR, "index.html")


@many_router.get("/index")
async def index():
    return FileResponse(INDEX_PATH)


def get_usd_rate():
    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    resp = requests.get(url, timeout=5)
    data = resp.json()
    return data["Valute"]["USD"]["Value"]

@many_router.websocket("/ws/usd")
async def ws_usd(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            rate = get_usd_rate()
            print(rate)
            await websocket.send_text(f"USD/RUB: {rate:.2f} ₽")
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        print("Клиент отключился")
    except Exception as e:
        print("Ошибка в сокете:", e)