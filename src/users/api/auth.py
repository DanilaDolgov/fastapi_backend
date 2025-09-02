from datetime import datetime, timezone, timedelta
from http.client import HTTPException

from fastapi import APIRouter, HTTPException, Response, Request
from passlib.context import CryptContext
import jwt



from src.database import async_session_maker
from src.hotels.api.dependencies import UserIdDep
from src.repositories.users import UsersRepository
from src.services.auth import AuthService
from src.users.schemas.users import UserRequestAdd, UserAdd
from src.config import settings

router = APIRouter(prefix='/auth', tags=["Авторизация и Аутентификация"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")




@router.post(path='/login')
async def login_user(
        data: UserRequestAdd,
        response: Response
):
    async with async_session_maker() as session:
        user = await UsersRepository(session).get_user_with_hashed_password(email=data.email)
        if not user:
            raise HTTPException(status_code=401, detail="User with this email not registration!")
        if not AuthService().verify_password(data.password, user.hash_password):
            raise HTTPException(status_code=401, detail="Password is not correct!")
        access_token =  AuthService().create_access_token({"user_id": user.id})
        response.set_cookie("access_token", access_token)
        return {'access_token': access_token}



@router.post(path='/register')
async def register_user(
        data: UserRequestAdd
):
    hashed_password = AuthService().hash_password(data.password)
    new_user_data = UserAdd(email=data.email, hash_password=hashed_password)
    async with async_session_maker() as session:
        await UsersRepository(session).add(new_user_data)
        await session.commit()
    return {'Status': 'Ok'}


@router.get("/me")
async def get_me(
user_id: UserIdDep
):
    async with async_session_maker() as session:
        user = await UsersRepository(session).get_one_or_none(id=user_id)
        return user


@router.post("/logout")
async def logout_user(response: Response):
    response.delete_cookie("access_token")
    return {'Status': 'Ok'}