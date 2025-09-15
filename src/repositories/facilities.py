from src.repositories.base import BaseRepository
from src.models.facilities import FacilitiesOrm, FacilitiesRoomsOrm
from src.schemas.facilities import Facilities, RoomsFacilities


class FacilitiesRepository(BaseRepository):
    model = FacilitiesOrm
    schema = Facilities


class RoomsFacilitiesRepository(BaseRepository):
    model = FacilitiesRoomsOrm
    schema = RoomsFacilities