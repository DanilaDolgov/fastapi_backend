from src.users.models.users import UsersOrm
from src.users.schemas.users import User
from src.repositories.base import BaseRepository


class UsersRepository(BaseRepository):
    model = UsersOrm
    schema = User


