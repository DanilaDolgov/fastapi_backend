from pydantic import EmailStr
from sqlalchemy import select

from src.users.models.users import UsersOrm
from src.users.schemas.users import User, UserHashPassword
from src.repositories.base import BaseRepository


class UsersRepository(BaseRepository):
    model = UsersOrm
    schema = User

    async def get_user_with_hashed_password(self, email: EmailStr):
        query = select(self.model).filter_by(email=email)
        result = await self.session.execute(query)
        model = result.scalars().one()
        return UserHashPassword.model_validate(model, from_attributes=True)


