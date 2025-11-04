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
    """
        Загрузка изображений для отеля или номера.

        Эта ручка позволяет загружать одно или несколько изображений в хранилище S3
        для сущностей `hotels` (отели) или `rooms` (номера).
        Перед загрузкой проверяется существование соответствующего объекта в базе данных.
        Если объект не найден, будет возвращена ошибка 404.
        Если файлы не переданы — ошибка 400.

        ---
        **Параметры пути:**
        - **entity** (`str`): тип сущности, для которой загружаются изображения.
          Возможные значения:
            - `"hotels"` — загрузка изображений для отеля
            - `"rooms"` — загрузка изображений для номера
        - **entity_id** (`int`): ID конкретного отеля или номера в базе данных.

        **Параметры тела запроса (form-data):**
        - **files** (`List[UploadFile]`): список загружаемых файлов (одно или несколько изображений).

        **Зависимости:**
        - **s3** (`S3Dep`): зависимость для работы с S3-хранилищем.
        - **db** (`DBDep`): зависимость для работы с базой данных.

        **Возвращает:**
        ```json
        {
            "Status": "Ok",
            "files upload": ["image1.jpg", "image2.png"]
        }
        ```

        **Ошибки:**
        - `400`: если указана неверная сущность (`entity` не "hotels" или "rooms")
        - `400`: если не переданы файлы
        - `404`: если отель или номер с данным ID не найден
        """
    if entity not in ("hotels", "rooms"):
        raise HTTPException(status_code=400, detail="Invalid entity. Must be 'hotels' or 'rooms'.")
    if entity == "hotels":
        obj = await db.hotels.get_one_or_none(id=entity_id)
    else:
        obj = await db.rooms.get_one_or_none(id=entity_id)

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
    result = [f.filename for f in file_dtos]

    return {"Status": "Ok", "files upload": f"{result}"}


