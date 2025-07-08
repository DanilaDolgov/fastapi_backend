from src.repositories.base import BaseRepository
from src.rooms.models.rooms import RoomsOrm


class RoomsRepository(BaseRepository):
    model = RoomsOrm