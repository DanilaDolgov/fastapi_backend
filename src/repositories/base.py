from operator import or_
from sqlalchemy.exc import NoResultFound
from pydantic import BaseModel
from sqlalchemy import select, insert, update, delete, and_
from sqlalchemy.exc import IntegrityError

from src.exceptions import HotelNotFoundException, FacilitiesNotFoundException, ObjectNotFoundException, \
    ObjectAlreadyExistsException
from src.repositories.mapper.base import DataMapper


class BaseRepository:
    model = None
    mapper: DataMapper = None

    def __init__(self, session):
        self.session = session

    async def get_all(self, *args, **kwargs):
        query = select(self.model)
        result = await self.session.execute(query)
        return [self.mapper.map_to_domain_entity(model) for model in result.scalars().all()]

    async def get_one(self, **kwargs):
        query = select(self.model).filter_by(**kwargs)
        result = await self.session.execute(query)
        print(query.compile(compile_kwargs={"literal_binds": True}))
        try:
            model = result.scalars().one()
        except NoResultFound:
            raise ObjectNotFoundException
        return self.mapper.map_to_domain_entity(model)

    async def get_one_or_none(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()
        if model:
            return self.mapper.map_to_domain_entity(model)
        return None

    async def get_in_params(self, *args, **filter_by):
        query = select(self.model).filter(*args).filter_by(**filter_by)
        result = await self.session.execute(query)
        if result:
            return [self.mapper.map_to_domain_entity(model) for model in result.scalars().all()]
        return None

    async def add(self, data: BaseModel):
        added_stm = insert(self.model).values(**data.model_dump()).returning(self.model)
        # print(added_stm.compile(compile_kwargs={"literal_binds": True}))
        try:
            result = await self.session.execute(added_stm)
            model = result.scalars().one()
            return self.mapper.map_to_domain_entity(model)
        except IntegrityError:
            raise ObjectAlreadyExistsException



    async def add_bulk(self, data: list[BaseModel]):
        added_stm = insert(self.model).values([item.model_dump() for item in data])
        print(added_stm.compile(compile_kwargs={"literal_binds": True}))
        try:
            await self.session.execute(added_stm)
        except IntegrityError:
            raise FacilitiesNotFoundException

    async def delete_bulk(self, data: list[BaseModel]):
        rows = [item.model_dump() for item in data]
        conditions = []
        for row in rows:
            cond = and_(*[getattr(self.model, k) == v for k, v in row.items()])
            conditions.append(cond)
        if not conditions:
            return
        elif len(conditions) == 1:
            final_condition = conditions[0]
        else:
            final_condition = or_(*conditions)

        delete_stm = delete(self.model).where(final_condition)

        print(delete_stm.compile(compile_kwargs={"literal_binds": True}))
        await self.session.execute(delete_stm)

    async def update(self, data: BaseModel, exclude_unset: bool = False, **filter_by) -> None:
        update_stm = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**data.model_dump(exclude_unset=exclude_unset))
        )

        await self.session.execute(update_stm)

    async def delete(self, **filter_by) -> None:
        delete_stm = delete(self.model).filter_by(**filter_by)
        await self.session.execute(delete_stm)
