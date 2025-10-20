from src.services.telegramm.base import ClientError, Client


class TgClientError(ClientError):
    pass


class TgClient(Client):
    BASE_PATH = 'https://api.telegram.org/bot'
    API_FILE_PATH = 'https://api.telegram.org/file/bot'

    def __init__(self, token: str = ''):
        self.token = token
        super().__init__()

    async def _handle_response(self, resp):
        return await resp.json()

    def get_path(self, url):
        return f'{self.get_base_path()}{self.token}/{url}'


    async def send_message(self, chat_id: int, text: str):
        params = {'chat_id': chat_id, 'text': text}
        await self._perform_request('post', self.get_path(f'sendMessage'), json=params)