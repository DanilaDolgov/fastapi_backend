from pydantic import BaseModel
from sqlalchemy import select, insert, update, delete
from sqlalchemy.orm import sessionmaker


class BaseRepository:
    model = None

    def __init__(self, session):
        self.session = session

    async def get_all(self, *args, **kwargs):
        query = select(self.model)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_one(self, **kwargs):
        query = select(self.model).filter_by(**kwargs)
        result = await self.session.execute(query)
        print(query.compile(compile_kwargs={"literal_binds": True}))
        return result.scalars().one_or_none()

    async def get_one_or_none(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def add(self, data: BaseModel):
        added_stm = insert(self.model).values(**data.model_dump()).returning(self.model)
        print(added_stm.compile(compile_kwargs={"literal_binds": True}))
        result = await self.session.execute(added_stm)
        return result.scalars().one()

    async def update(self, data: BaseModel, exclude_unset: bool = False,**filter_by) -> None :
        update_stm = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**data.model_dump(exclude_unset=exclude_unset)))

        await self.session.execute(update_stm)

    async def delete(self, **filter_by) -> None:
        delete_stm =delete(self.model).filter_by(**filter_by)
        await self.session.execute(delete_stm)