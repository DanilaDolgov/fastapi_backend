from pydantic import BaseModel
from sqlalchemy import select, insert, update, delete
from sqlalchemy.orm import sessionmaker

from src.hotels.schemas.hotels import Hotel


class BaseRepository:
    model = None
    schema: BaseModel = None

    def __init__(self, session):
        self.session = session

    async def get_all(self, *args, **kwargs):
        query = select(self.model)
        result = await self.session.execute(query)
        return [self.schema.model_validate(model, from_attributes=True) for model in result.scalars().all()]

    async def get_one(self, **kwargs):
        query = select(self.model).filter_by(**kwargs)
        result = await self.session.execute(query)
        print(query.compile(compile_kwargs={"literal_binds": True}))
        model = result.scalars().one_or_none()
        if model:
            return self.schema.model_validate(model, from_attributes=True)
        return None

    async def get_one_or_none(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()
        if model:
            return self.schema.model_validate(model, from_attributes=True)
        return None

    async def add(self, data: BaseModel):
        added_stm = insert(self.model).values(**data.model_dump()).returning(self.model)
        print(added_stm.compile(compile_kwargs={"literal_binds": True}))
        result = await self.session.execute(added_stm)
        model = result.scalars().one()
        return self.schema.model_validate(model, from_attributes=True)


    async def update(self, data: BaseModel, exclude_unset: bool = False,**filter_by) -> None :
        update_stm = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**data.model_dump(exclude_unset=exclude_unset)))

        await self.session.execute(update_stm)

    async def delete(self, **filter_by) -> None:
        delete_stm =delete(self.model).filter_by(**filter_by)
        await self.session.execute(delete_stm)