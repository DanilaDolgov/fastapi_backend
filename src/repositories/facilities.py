from src.repositories.base import BaseRepository
from src.models.facilities import FacilitiesOrm, FacilitiesRoomsOrm
from src.repositories.mapper.mapper import FacilitiesDataMapper, RoomFacilitiesDataMapper
from src.schemas.facilities import Facilities, RoomsFacilities


class FacilitiesRepository(BaseRepository):
    model = FacilitiesOrm
    mapper = FacilitiesDataMapper


class RoomsFacilitiesRepository(BaseRepository):
    model = FacilitiesRoomsOrm
    mapper = RoomFacilitiesDataMapper