from src.models.telegramm import TelegrammChatOrm
from src.repositories.base import BaseRepository
from src.repositories.mapper.mapper import TelegrammDataMapper


class TelegrammRepository(BaseRepository):
    model = TelegrammChatOrm
    mapper = TelegrammDataMapper