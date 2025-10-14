import json
from datetime import date
from fastapi import APIRouter, File, UploadFile, Query, Form, HTTPException
from typing import List
from sqlalchemy.exc import IntegrityError

from src.dependencies.dependencies import DBDep, S3Dep
from src.schemas.facilities import RoomsFacilitiesAdd
from src.schemas.rooms import RoomAdd, RoomPATCH, RoomAddRequest, RoomPatchRequest

router_rooms = APIRouter(prefix="/rooms", tags=["Rooms"])


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
        [RoomsFacilitiesAdd(rooms_id=room_id, facilities_id=x) for x in list2 if x not in list1]
    )


@router_rooms.post("/{hotel_id}")
async def create_rooms(
    hotel_id: int,
    s3: S3Dep,
    db: DBDep,
    data_room_str: str = Form(..., description=json.dumps({
        "title": "string",
        "description": "string",
        "price": 0,
        "quantity": 0,
        "facilities_ids": [1, 2]
    })),
    files: List[UploadFile] | None = File(None)
):
    """
    Create a new room for a specific hotel.

    Args:
        hotel_id (int): The ID of the hotel the room belongs to.
        s3 (S3Dep): S3 dependency for file storage operations.
        db (DBDep): Database dependency.
        data_room_str (str): JSON string containing room data (via form submission).
        files (List[UploadFile], optional): List of room image files to upload.

    Returns:
        dict: Operation status and details of the created room.

    Example:
        {
            "Status": "Ok",
            "data": {
                "title": "Luxury Suite",
                "description": "Spacious room with a sea view",
                "price": 15000,
                "quantity": 3
            }
        }
    """
    data_room = RoomAddRequest(**json.loads(data_room_str))
    _res = RoomAdd(hotel_id=hotel_id, **data_room.model_dump())
    room = await db.rooms.add(_res)
    rooms_facilities = [RoomsFacilitiesAdd(rooms_id=room.id, facilities_id=r) for r in data_room.facilities_ids]
    await db.rooms_facilities.add_bulk(rooms_facilities)
    await db.commit()

    if files:
        for file in files:
            s3_key = f"rooms/{room.id}/{file.filename}"
            await s3.upload_file(file=file, s3_key=s3_key)

    return {
        'Status': 'Ok',
        'data': {
            'title': room.title,
            'description': room.description,
            'price': room.price,
            'quantity': room.quantity
        }
    }


@router_rooms.get("/{hotel_id}/{room_id}")
async def get_room_one(hotel_id: int, s3: S3Dep, db: DBDep, room_id: int):
    """
    Retrieve detailed information about a single room, including its images.

    Args:
        hotel_id (int): The ID of the hotel.
        s3 (S3Dep): S3 dependency for file storage operations.
        db (DBDep): Database dependency.
        room_id (int): The ID of the room.

    Returns:
        dict: Room details and a list of image URLs.
    """
    room = await db.rooms.get_one_or_none(id=room_id, hotel_id=hotel_id)
    path = f'rooms/{room_id}/'
    urls_image = await s3.generate_presigned_urls_by_prefix(prefix=path)

    return {'Room': room, 'image': urls_image}


@router_rooms.get("/{hotel_id}")
async def get_rooms(
    hotel_id: int,
    s3: S3Dep,
    db: DBDep,
    date_from: date = Query(example="2025-09-20"),
    date_to: date = Query(example="2025-09-30")
):
    """
    Retrieve a list of available rooms in a hotel for a specific date range.

    Args:
        hotel_id (int): The ID of the hotel.
        s3 (S3Dep): S3 dependency for file storage operations.
        db (DBDep): Database dependency.
        date_from (date): Start date of the range.
        date_to (date): End date of the range.

    Returns:
        dict: List of available rooms with their images, or 'empty' if none are found.
    """
    rooms = await db.rooms.get_filtered_by_time(hotel_id=hotel_id, date_from=date_from, date_to=date_to)
    if rooms:
        data_rooms = [
            {'room_id': room.id, room.id: {
                'data_room': room,
                'images': await s3.generate_presigned_urls_by_prefix(prefix=f'rooms/{room.id}/')
            }}
            for room in rooms
        ]
        return {'Status': 'Ok', 'rooms': data_rooms}
    else:
        return {'Status': 'Ok', 'data': 'empty'}


@router_rooms.delete("/{hotel_id}/{room_id}")
async def delete_room(db: DBDep, s3: S3Dep, hotel_id: int, room_id: int):
    """
    Delete a room and its associated images from storage.

    Args:
        db (DBDep): Database dependency.
        s3 (S3Dep): S3 dependency for file storage operations.
        hotel_id (int): The ID of the hotel.
        room_id (int): The ID of the room.

    Returns:
        dict: Operation status.
    """
    await db.rooms.delete(id=room_id, hotel_id=hotel_id)
    await db.commit()
    path = f'rooms/{room_id}'
    await s3.delete_files(path)

    return {'Status': 'Ok'}


@router_rooms.put("/{hotel_id}/{room_id}")
async def update_room(db: DBDep, hotel_id: int, room_id: int, data_room: RoomAddRequest):
    """
    Fully update room information and its facilities.

    Args:
        db (DBDep): Database dependency.
        hotel_id (int): The ID of the hotel.
        room_id (int): The ID of the room.
        data_room (RoomAddRequest): New data for the room.

    Raises:
        HTTPException: If one or more provided facility IDs do not exist.

    Returns:
        dict: Operation status.
    """
    _res = RoomAdd(hotel_id=hotel_id, **data_room.model_dump())
    await db.rooms.update(_res, id=room_id)
    try:
        if data_room.facilities_ids and 0 not in data_room.facilities_ids:
            facilities_ids = [
                facility_id.facilities_id for facility_id in await db.rooms_facilities.get_in_params(rooms_id=room_id)
            ]
            del_facilities_ids, add_facilities_ids = unique_diff_room_facilities(
                room_id, facilities_ids, data_room.facilities_ids
            )
            if add_facilities_ids:
                await db.rooms_facilities.add_bulk(add_facilities_ids)
            if del_facilities_ids:
                await db.rooms_facilities.delete_bulk(del_facilities_ids)
        await db.commit()
    except IntegrityError:
        await db.session.rollback()
        raise HTTPException(status_code=400, detail="One of the facilities_id does not exist")

    return {'Status': 'Ok'}


@router_rooms.patch("/{hotel_id}/{room_id}")
async def update_patch_room(db: DBDep, hotel_id: int, room_id: int, data_room: RoomPatchRequest):
    """
    Partially update room data and its facilities.

    Args:
        db (DBDep): Database dependency.
        hotel_id (int): The ID of the hotel.
        room_id (int): The ID of the room.
        data_room (RoomPatchRequest): Partial data for updating the room.

    Returns:
        dict: Operation status.
    """
    _res = RoomPATCH(hotel_id=hotel_id, **data_room.model_dump(exclude_unset=True))
    await db.rooms.update(_res, exclude_unset=True, id=room_id)

    if data_room.facilities_ids:
        facilities_ids = [
            facility_id.facilities_id for facility_id in await db.rooms_facilities.get_in_params(rooms_id=room_id)
        ]
        del_facilities_ids, add_facilities_ids = unique_diff_room_facilities(
            room_id, facilities_ids, data_room.facilities_ids
        )
        if add_facilities_ids:
            await db.rooms_facilities.add_bulk(add_facilities_ids)
        if del_facilities_ids:
            await db.rooms_facilities.delete_bulk(del_facilities_ids)

    await db.commit()
    return {'Status': 'Ok'}
