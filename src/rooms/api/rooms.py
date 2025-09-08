from fastapi import  APIRouter, File, UploadFile, Depends
from typing import List

from src.database import async_session_maker
from src.services.s3 import S3Client
from src.repositories.rooms import RoomsRepository
from src.rooms.schemas.rooms import RoomAdd, RoomPATCH, RoomForm, RoomPatchRequest, as_form

router_rooms = APIRouter(prefix="/rooms", tags=["Номера"])



@router_rooms.post("/{hotel_id}")
async def create_rooms(
        hotel_id: int,
        data_room: RoomForm = Depends(as_form),
        files: List[UploadFile] | None = File(None)):
    _res = RoomAdd(
        hotel_id=hotel_id,
        **data_room.model_dump()
    )
    async with async_session_maker() as session:
        room = await RoomsRepository(session).add(_res)
        await session.commit()
    if files:
        for file in files:
            s3_key = f"rooms/{room.id}/{file.filename}"
            await S3Client().upload_file(file=file, s3_key=s3_key)


    return {'Status': 'Ok', 'data': {'title': room.title,
                                     'description': room.description,
                                     'price': room.price,
                                     'quantity': room.quantity}}


@router_rooms.get("/{hotel_id}/{room_id}")
async def get_room_one(hotel_id: int, room_id: int):
    async with async_session_maker() as session:
        room = await RoomsRepository(session).get_one_or_none(id=room_id, hotel_id=hotel_id)
        path = f'rooms/{room_id}'
        urls_image = await S3Client().generate_presigned_urls_by_prefix(prefix=path)
        return {'Room': room, 'image': urls_image}

@router_rooms.delete("/{hotel_id}/{room_id}")
async def delete_room(hotel_id: int, room_id: int):
    async with async_session_maker() as session:
        await RoomsRepository(session).delete(id=room_id, hotel_id= hotel_id)
        await session.commit()
        path = f'rooms/{room_id}'
        await S3Client().delete_files(path)

    return {'Status': 'Ok'}

@router_rooms.put("/{hotel_id}/{room_id}")
async def update_room(hotel_id: int, room_id: int, data_room: RoomForm):
    _res = RoomAdd(hotel_id= hotel_id, **data_room.model_dump())
    async with async_session_maker() as session:
        await RoomsRepository(session).update(_res, id=room_id )
        await session.commit()
    return {'Status': 'Ok'}

@router_rooms.patch("/{hotel_id}/{room_id}")
async def update_patch_room(hotel_id: int, room_id: int, data_room: RoomPatchRequest):
    _res = RoomPATCH(hotel_id=hotel_id, **data_room.model_dump(exclude_unset=True))
    async with async_session_maker() as session:
        await RoomsRepository(session).update(_res, exclude_unset=True, id=room_id)
        await session.commit()

    return {'Status': 'Ok'}