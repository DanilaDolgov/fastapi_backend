from fastapi import Query, APIRouter, Body
from src.database import async_session_maker
from src.hotels.api.dependencies import PaginationHotels, PaginationRooms
# from src.hotels.schemas.hotels import Hotel, HotelPATCH, HotelAdd
from src.repositories.rooms import RoomsRepository
from src.rooms.schemas.rooms import RoomAdd, RoomPATCH

router_rooms = APIRouter(prefix="/rooms", tags=["Номера"])



@router_rooms.post("")
async def create_rooms(data_rooms: RoomAdd):
    async with async_session_maker() as session:
        room = await RoomsRepository(session).add(data_rooms)
        await session.commit()
    return {'Status': 'Ok', 'data': room}


@router_rooms.get("/{room_id}")
async def get_room_one(room_id: int):
    async with async_session_maker() as session:
        room = await RoomsRepository(session).get_one_or_none(id=room_id)
        return {'Room': room}

@router_rooms.delete("/{room_id}")
async def delete_room(room_id: int):
    async with async_session_maker() as session:
        await RoomsRepository(session).delete(id=room_id)
        await session.commit()

    return {'Status': 'Ok'}

@router_rooms.put("/{room_id}")
async def update_room(room_id: int, data_room: RoomAdd):
    async with async_session_maker() as session:
        await RoomsRepository(session).update(data_room, id=room_id)
        await session.commit()
    return {'Status': 'Ok'}

@router_rooms.patch("/{room_id}")
async def update_patch_room(room_id: int, data_room: RoomPATCH):
    async with async_session_maker() as session:
        await RoomsRepository(session).update(data_room, exclude_unset=True, id=room_id)
        await session.commit()

    return {'Status': 'Ok'}

@router_rooms.get("")
async def get_rooms(
        pagination: PaginationRooms,
        title: str | None = Query(None, description="Тип номера.")
):
    per_page = pagination.per_page or 5
    async with async_session_maker() as session:
       return await RoomsRepository(session=session).get_all(
            title=title,
            limit=per_page,
            offset=per_page * (pagination.page - 1))