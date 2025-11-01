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
from src.services.Images import ImageServices
from src.services.rooms import RoomServices
from src.utils.s3_settings import s3_manager

router_images = APIRouter(prefix="/images", tags=["IMAGES"])



@router_images.post("/{entity}/{entity_id}")
async def upload_images(entity: str, entity_id: int, s3: S3Dep, db: DBDep, files: List[UploadFile]):
    if entity not in ("hotels", "rooms"):
        raise HTTPException(status_code=400, detail="Invalid entity. Must be 'hotels' or 'rooms'.")
    if entity == "hotels":
        obj = await db.hotels.get_one(id=entity_id)
    else:
        obj = await db.rooms.get_one(id=entity_id)

    if not obj:
        raise HTTPException(status_code=404, detail=f"{entity[:-1].capitalize()} not found")

    if not files or len(files) == 0:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    file_dtos = [
        FileDTO(
            filename=f.filename,
            content_type=f.content_type,
            file=BufferedReader(f.file)
        )
        for f in files
    ]

    await ImageServices(s3=s3_manager).image_upload(file_dtos=file_dtos, path=f"/{entity}/{entity_id}")


