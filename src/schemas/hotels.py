from pydantic import BaseModel, Field, field_validator


class HotelAdd(BaseModel):
    title: str = Field(..., min_length=5, description="Name hotel can not empty.")
    location: str = Field(..., min_length=1, description="Name hotel can not empty.")

    @field_validator("title")
    def validate_title(cls, v: str):
        v = v.strip()
        if not v:
            raise ValueError("Название отеля не может быть пустым или состоять из пробелов.")
        if len(v) < 5:
            raise ValueError("Название отеля должно содержать минимум 5 символов.")
        return v

    @field_validator("location")
    def validate_location(cls, v: str):
        v = v.strip()
        if not v:
            raise ValueError("Адрес не может быть пустым.")
        return v


class Hotel(HotelAdd):
    id: int


class HotelPATCH(BaseModel):
    title: str | None = Field(None, min_length=1, description="Name hotel can not empty.")
    location: str | None = Field(None, min_length=1, description="Name hotel can not empty.")

    @field_validator("title")
    def validate_title(cls, v: str):
        v = v.strip()
        if not v:
            raise ValueError("Название отеля не может быть пустым или состоять из пробелов.")
        if len(v) < 5:
            raise ValueError("Название отеля должно содержать минимум 5 символов.")
        return v

    @field_validator("location")
    def validate_location(cls, v: str):
        v = v.strip()
        if not v:
            raise ValueError("Адрес не может быть пустым.")
        return v

