from fastapi import  APIRouter, File, UploadFile, Depends
from typing import List

from src.dependencies.dependencies import DBDep, S3Dep
from src.services.s3 import S3Client
from src.schemas.rooms import RoomAdd, RoomPATCH, RoomForm, RoomPatchRequest, as_form

router_rooms = APIRouter(prefix="/rooms", tags=["Номера"])



@router_rooms.post("/{hotel_id}")
async def create_rooms(
        hotel_id: int,
        s3: S3Dep,
        db: DBDep,
        data_room: RoomForm = Depends(as_form),
        files: List[UploadFile] | None = File(None)):
    _res = RoomAdd(
        hotel_id=hotel_id,
        **data_room.model_dump()
    )
    room = await db.rooms.add(_res)
    await db.commit()
    if files:
        for file in files:
            s3_key = f"rooms/{room.id}/{file.filename}"
            await s3.upload_file(file=file, s3_key=s3_key)

    return {'Status': 'Ok', 'data': {'title': room.title,
                                     'description': room.description,
                                     'price': room.price,
                                     'quantity': room.quantity}}


@router_rooms.get("/{hotel_id}/{room_id}")
async def get_room_one(hotel_id: int, s3: S3Dep, db: DBDep, room_id: int):
    room = await db.rooms.get_one_or_none(id=room_id, hotel_id=hotel_id)
    path = f'rooms/{room_id}'
    urls_image = await s3.generate_presigned_urls_by_prefix(prefix=path)

    return {'Room': room, 'image': urls_image}

@router_rooms.delete("/{hotel_id}/{room_id}")
async def delete_room(db: DBDep, s3: S3Dep, hotel_id: int, room_id: int):
    await db.rooms.delete(id=room_id, hotel_id= hotel_id)
    await db.commit()
    path = f'rooms/{room_id}'
    await s3.delete_files(path)

    return {'Status': 'Ok'}

@router_rooms.put("/{hotel_id}/{room_id}")
async def update_room(db: DBDep, hotel_id: int, room_id: int, data_room: RoomForm):
    _res = RoomAdd(hotel_id= hotel_id, **data_room.model_dump())
    await db.rooms.update(_res, id=room_id)
    await db.commit()

    return {'Status': 'Ok'}

@router_rooms.patch("/{hotel_id}/{room_id}")
async def update_patch_room(db: DBDep, hotel_id: int, room_id: int, data_room: RoomPatchRequest):
    _res = RoomPATCH(hotel_id=hotel_id, **data_room.model_dump(exclude_unset=True))
    await db.rooms.update(_res, exclude_unset=True, id=room_id)
    await db.commit()

    return {'Status': 'Ok'}