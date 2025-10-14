from pydantic import EmailStr
from sqlalchemy import select

from src.models.users import UsersOrm
from src.repositories.mapper.mapper import UserDataMapper
from src.schemas.users import UserHashPassword
from src.repositories.base import BaseRepository


class UsersRepository(BaseRepository):
    model = UsersOrm
    mapper = UserDataMapper

    async def get_user_with_hashed_password(self, email: EmailStr):
        query = select(self.model).filter_by(email=email)
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()
        if model:
            return UserHashPassword.model_validate(model, from_attributes=True)
        else:
            return None
