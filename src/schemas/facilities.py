from pydantic import BaseModel


class FacilitiesRequest(BaseModel):
    title: str


class Facilities(FacilitiesRequest):
    id: int


class RoomsFacilitiesAdd(BaseModel):
    facilities_id: int
    rooms_id: int


class RoomsFacilities(RoomsFacilitiesAdd):
    id: int
