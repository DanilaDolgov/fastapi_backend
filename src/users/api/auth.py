from fastapi import APIRouter
from passlib.context import CryptContext
from sqlalchemy.util import deprecated

from src.database import async_session_maker
from src.repositories.users import UsersRepository
from src.users.schemas.users import UserRequestAdd, UserAdd

router = APIRouter(prefix='/auth', tags=["Авторизация и Аутентификация"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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