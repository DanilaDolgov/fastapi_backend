from datetime import date
from typing import List

from src.dependencies.dependencies import Pagination
from src.schemas.bookings import BookingRequest, BookingAdd
from src.schemas.facilities import RoomsFacilitiesAdd
from src.schemas.files_dto import FileDTO
from src.schemas.rooms import RoomAdd, RoomAddRequest, RoomPATCH, RoomPatchRequest
from src.services.base import BaseServices

def unique_diff_room_facilities(room_id: int, list1: list, list2: list):
    """
    Compare two lists of facility IDs and return differences as RoomsFacilitiesAdd objects.

    Args:
        room_id (int): Room ID.
        list1 (list): Existing facility IDs in the database.
        list2 (list): New list of facility IDs provided by the user.

    Returns:
        tuple:
            - List of RoomsFacilitiesAdd objects to add.
            - List of RoomsFacilitiesAdd objects to delete.
    """
    return (
        [RoomsFacilitiesAdd(rooms_id=room_id, facilities_id=x) for x in list1 if x not in list2],
        [RoomsFacilitiesAdd(rooms_id=room_id, facilities_id=x) for x in list2 if x not in list1],
    )


class BookingServices(BaseServices):
    async def create_booking(self,
            data_booking: BookingRequest,
            user_id: int,
    ):
        room = await self.db.rooms.get_one(id=data_booking.room_id)
        _res = BookingAdd(user_id=user_id, **data_booking.model_dump(), price=room.price)
        booking = await self.db.booking.add_booking(_res)
        await self.db.commit()
        return booking

    async def get_bookings(self, pagination: Pagination):
        per_page = pagination.per_page or 5
        bookings = await self.db.booking.get_all(limit=per_page, offset=per_page * (pagination.page - 1))
        return bookings

    async def get_booking_for_me(self, user_id: int):
        booking =  await self.db.booking.get_in_params(user_id=user_id)
        return booking

    async def get_users_checkin_in_rooms_today(self):
        results_bookings = await self.db.booking.user_checkin_room_email()
        for result_booking in results_bookings:
            result_booking["images"] = await self.s3.generate_presigned_urls_by_prefix(
                prefix=f"rooms/{result_booking['room_id']}/"
            )
        return results_bookings
