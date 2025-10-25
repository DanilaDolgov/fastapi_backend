import json
from datetime import date
from io import BufferedReader

from fastapi import APIRouter, File, UploadFile, Query, Form, HTTPException
from typing import List

from fastapi.params import Depends
from sqlalchemy.exc import IntegrityError

from src.dependencies.dependencies import DBDep, hotel_not_none, get_s3_client, S3Dep
from src.exceptions import HotelNotFoundException, FacilitiesNotFoundException, \
    NotCorrectDateException, ObjectNotFoundException
from src.schemas.facilities import RoomsFacilitiesAdd
from src.schemas.files_dto import FileDTO
from src.schemas.rooms import RoomAdd, RoomPATCH, RoomAddRequest, RoomPatchRequest
from src.dependencies.dependencies import room_not_none
from src.services.rooms import RoomServices
from src.utils.s3_settings import s3_manager

router_rooms = APIRouter(prefix="/rooms", tags=["Rooms"])



@router_rooms.post("/{hotel_id}")
async def create_rooms(
    hnn: hotel_not_none,
    hotel_id: int,
    db: DBDep,
    data_room_str: str = Form(
        ...,
        description=json.dumps(
            {
                "title": "string",
                "description": "string",
                "price": 0,
                "quantity": 0,
                "facilities_ids": [1, 2],
            }
        ),
    ),
    files: List[UploadFile] | None = File(None),
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

    if hnn:
        data_room = RoomAddRequest(**json.loads(data_room_str))
        _res = RoomAdd(hotel_id=hotel_id, **data_room.model_dump())
        if files:
            file_dtos = [
                FileDTO(
                    filename=f.filename,
                    content_type=f.content_type,
                    file=BufferedReader(f.file)
                )
                for f in files
            ]
            print(file_dtos)
        try:
            room = await RoomServices(db, s3=s3_manager).create_rooms(_res, data_room, file_dtos)
        except FacilitiesNotFoundException as e:
            raise HTTPException(status_code=400, detail=e.detail)

        return {
            "Status": "Ok",
            "data": {
                "title": room.title,
                "description": room.description,
                "price": room.price,
                "quantity": room.quantity,
            },
        }


@router_rooms.get("/{hotel_id}/{room_id}")
async def get_room_one(hotel_id: int, db: DBDep, room_id: int, hnn: hotel_not_none, rnn: room_not_none):
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
    if hnn and rnn:
        result = await RoomServices(db, s3=s3_manager).get_room_one(room_id=room_id, hotel_id=hotel_id)
        return result


#
#
@router_rooms.get("/{hotel_id}")
async def get_rooms(
    hnn: hotel_not_none,
    hotel_id: int,
    db: DBDep,
    date_from: date = Query(example="2025-09-20"),
    date_to: date = Query(example="2025-09-30"),
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
    if hnn:
        try:
            rooms = await RoomServices(db, s3=s3_manager).get_all_rooms(hotel_id=hotel_id,
                                                             date_to=date_to,
                                                             date_from=date_from)
        except NotCorrectDateException as ex:
            raise HTTPException(status_code=400, detail=ex.detail)

        return rooms


@router_rooms.delete("/{hotel_id}/{room_id}")
async def delete_room(db: DBDep, s3: S3Dep, hotel_id: int, room_id: int, hnn: hotel_not_none, rnn: room_not_none):
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
    if hnn and rnn:
        await RoomServices(db, s3=s3_manager).delete_room(room_id=room_id,
                                                          hotel_id=hotel_id)

        return {"Status": "Ok"}


@router_rooms.put("/{hotel_id}/{room_id}")
async def update_room(db: DBDep,
                      hotel_id: int,
                      room_id: int,
                      data_room: RoomAddRequest,
                      hnn: hotel_not_none,
                      rnn: room_not_none):
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
    if hnn and rnn:
        _res = RoomAdd(hotel_id=hotel_id, **data_room.model_dump())
        try:
            await RoomServices(db).update_room(room_id=room_id, res=_res, data_room=data_room)
        except IntegrityError:
            await db.session.rollback()
            raise HTTPException(status_code=400, detail="One of the facilities_id does not exist")

        return {"Status": "Ok"}


@router_rooms.patch("/{hotel_id}/{room_id}")
async def update_patch_room(db: DBDep,
                            hotel_id: int,
                            room_id: int,
                            file_path: str | None,
                            data_room: RoomPatchRequest,
                            hnn: hotel_not_none,
                            rnn: room_not_none):
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
    if hnn and rnn:
        _res = RoomPATCH(hotel_id=hotel_id, **data_room.model_dump(exclude_unset=True))
        await RoomServices(db).patch_room(room_id=room_id, res=_res, data_room=data_room, file_path=file_path)
        return {"Status": "Ok"}
