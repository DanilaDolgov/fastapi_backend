from pydantic import BaseModel, EmailStr, Field


class UserRequestAdd(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, description="Пароль не может быть пустым")


class UserAdd(BaseModel):
    email: EmailStr
    hash_password: str


class User(BaseModel):
    id: int
    email: EmailStr


class UserHashPassword(User):
    hash_password: str
