import ssl
from typing import Any

import aiohttp
import certifi
from aiohttp import ClientResponse


class ClientError(Exception):
    def __init__(self, response: ClientResponse, content: Any = None):
        self.response = response
        self.content = content


class Client:
    BASE_PATH = 'https://api.telegram.org/bot'
    API_FILE_PATH = 'https://api.telegram.org/file/bot'

    def __init__(self):
        # Создаём SSL-контекст с доверенными сертификатами
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        self.session = aiohttp.ClientSession(connector=connector)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    def get_base_path(self) -> str:
        return self.BASE_PATH.strip('/')

    def get_path(self, url: str) -> str:
        base_path = self.get_base_path().strip('/')
        url = url.lstrip('/')
        return f'{base_path}/{url}'

    async def _handle_response(self, resp: ClientResponse) -> Any:
        return resp

    async def _perform_request(self, method: str, url: str, **kwargs) -> Any:
        async with self.session.request(method, url, **kwargs) as resp:
            return await self._handle_response(resp)
