from src.models.bookings import BookingsOrm
from src.models.facilities import FacilitiesOrm, FacilitiesRoomsOrm
from src.models.hotels import HotelsOrm
from src.models.rooms import RoomsOrm
from src.models.telegramm import TelegrammChatOrm
from src.models.users import UsersOrm
from src.repositories.mapper.base import DataMapper
from src.schemas.bookings import Booking
from src.schemas.facilities import Facilities, RoomsFacilities
from src.schemas.hotels import Hotel
from src.schemas.rooms import Room
from src.schemas.telegramm import TelegrammChatBase
from src.schemas.users import User


class HotelDataMapper(DataMapper):
    db_model = HotelsOrm
    schema = Hotel


class FacilitiesDataMapper(DataMapper):
    db_model = FacilitiesOrm
    schema = Facilities


class RoomDataMapper(DataMapper):
    db_model = RoomsOrm
    schema = Room


class RoomFacilitiesDataMapper(DataMapper):
    db_model = FacilitiesRoomsOrm
    schema = RoomsFacilities


class UserDataMapper(DataMapper):
    db_model = UsersOrm
    schema = User


class BookingDataMapper(DataMapper):
    db_model = BookingsOrm
    schema = Booking

class TelegrammDataMapper(DataMapper):
    db_model = TelegrammChatOrm
    schema = TelegrammChatBase
