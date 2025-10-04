from src.models.facilities import FacilitiesOrm
from src.models.hotels import HotelsOrm
from src.repositories.mapper.base import DataMapper
from src.schemas.facilities import Facilities
from src.schemas.hotels import Hotel


class HotelDataMapper(DataMapper):
    db_model = HotelsOrm
    schema = Hotel

class FacilitiesDataMapper(DataMapper):
    db_model = FacilitiesOrm
    schema = Facilities