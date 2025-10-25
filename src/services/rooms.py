from datetime import date
from typing import List

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


class RoomServices(BaseServices):
    async def create_rooms(self,
            room_data_add: RoomAdd,
            room_data_request: RoomAddRequest,
            file_dtos: List[FileDTO] | None = None,
    ):
        room = await self.db.rooms.add(room_data_add)
        rooms_facilities = [
            RoomsFacilitiesAdd(rooms_id=room.id, facilities_id=r) for r in room_data_request.facilities_ids
        ]
        await self.db.rooms_facilities.add_bulk(rooms_facilities)
        await self.db.commit()
        if file_dtos:
            s3_key = f"rooms/{room.id}"
            await self.s3.upload_files( files=file_dtos, prefix=s3_key)
        return room

    async def get_room_one(self, room_id: int, hotel_id: int):
        room = await self.db.rooms.get_one(id=room_id, hotel_id=hotel_id)
        path = f"rooms/{room_id}/"
        urls_image = await self.s3.generate_presigned_urls_by_prefix(prefix=path)
        return {"Room": room, "image": urls_image}

    async def get_all_rooms(self,
                            hotel_id: int,
                            date_from: date,
                            date_to: date):

        rooms = await self.db.rooms.get_filtered_by_time(
            hotel_id=hotel_id, date_from=date_from, date_to=date_to
        )

        data_rooms = [
            {
                "room_id": room.id,
                room.id: {
                    "data_room": room,
                    "images": await self.s3.generate_presigned_urls_by_prefix(prefix=f"rooms/{room.id}/"),
                },
            }
            for room in rooms
        ]
        return {"Status": "Ok", "rooms": data_rooms}

    async def delete_room(self, room_id, hotel_id):
        await self.db.rooms.delete_rooms(room_id=room_id, hotel_id=hotel_id)
        await self.db.commit()
        path = f"rooms/{room_id}"
        await self.s3.delete_files(prefix=path)

    async def update_room(self, room_id, res: RoomAdd, data_room: RoomAddRequest):
        await self.db.rooms.update(res, id=room_id)
        if data_room.facilities_ids and 0 not in data_room.facilities_ids:
            facilities_ids = [
                facility_id.facilities_id
                for facility_id in await self.db.rooms_facilities.get_in_params(rooms_id=room_id)
            ]
            del_facilities_ids, add_facilities_ids = unique_diff_room_facilities(
                room_id, facilities_ids, data_room.facilities_ids
            )
            if add_facilities_ids:
                await self.db.rooms_facilities.add_bulk(add_facilities_ids)
            if del_facilities_ids:
                await self.db.rooms_facilities.delete_bulk(del_facilities_ids)
        await self.db.commit()

    async def patch_room(self, room_id, res: RoomPATCH, data_room: RoomPatchRequest, filename: str | None = None):
        await self.db.rooms.update(res, exclude_unset=True, id=room_id)
        if data_room.facilities_ids:
            facilities_ids = [
                facility_id.facilities_id
                for facility_id in await self.db.rooms_facilities.get_in_params(rooms_id=room_id)
            ]
            del_facilities_ids, add_facilities_ids = unique_diff_room_facilities(
                room_id, facilities_ids, data_room.facilities_ids
            )
            if add_facilities_ids:
                await self.db.rooms_facilities.add_bulk(add_facilities_ids)
            if del_facilities_ids:
                await self.db.rooms_facilities.delete_bulk(del_facilities_ids)

        await self.db.commit()
        if filename:
            await self.s3.delete_files(filename)
