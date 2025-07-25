from datetime import datetime, timezone, timedelta
from http.client import HTTPException

from fastapi import APIRouter, HTTPException, Response
from passlib.context import CryptContext
import jwt



from src.database import async_session_maker
from src.repositories.users import UsersRepository
from src.users.schemas.users import UserRequestAdd, UserAdd

router = APIRouter(prefix='/auth', tags=["Авторизация и Аутентификация"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

@router.post(path='/login')
async def login_user(
        data: UserRequestAdd,
        response: Response
):
    async with async_session_maker() as session:
        user = await UsersRepository(session).get_user_with_hashed_password(email=data.email)
        if not user:
            raise HTTPException(status_code=401, detail="User with this email not registration!")
        if not verify_password(data.password, user.hash_password):
            raise HTTPException(status_code=401, detail="Password is not correct!")
        access_token =  create_access_token({"user_id": user.id})
        response.set_cookie("access_token", access_token)
        return {'access_token': access_token}



@router.post(path='/register')
async def register_user(
        data: UserRequestAdd
):
    hashed_password = pwd_context.hash(data.password)
    new_user_data = UserAdd(email=data.email, hash_password=hashed_password)
    async with async_session_maker() as session:
        await UsersRepository(session).add(new_user_data)
        await session.commit()
    return {'Status': 'Ok'}

