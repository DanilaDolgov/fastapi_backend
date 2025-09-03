from src.repositories.base import BaseRepository
from src.rooms.models.rooms import RoomsOrm
from src.rooms.schemas.rooms import Room, RoomShow


class RoomsRepository(BaseRepository):
    model = RoomsOrm
    schema = RoomShow