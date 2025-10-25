import logging
from datetime import datetime
from operator import or_

from asyncpg import UniqueViolationError
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy import select, insert, update, delete, and_
from pydantic import BaseModel

from src.exceptions import FacilitiesNotFoundException, ObjectNotFoundException, ObjectAlreadyExistsException
from src.repositories.mapper.base import DataMapper



def notify_on_error(func):
    import functools

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as ex:
            if isinstance(ex, (ObjectAlreadyExistsException, ObjectNotFoundException, FacilitiesNotFoundException)):
                raise

            import logging
            from datetime import datetime
            from src.tasks.tasks import send_in_telegram

            logging.error(f"Unexpected error in {func.__name__}: {ex}", exc_info=True)
            send_in_telegram.delay(f"{datetime.now()}\nUnexpected error in {func.__name__}: {ex}")
            raise

    return wrapper



class BaseRepository:
    model = None
    mapper: DataMapper = None

    def __init__(self, session):
        self.session = session

    @notify_on_error
    async def get_all(self, *args, **kwargs):
        query = select(self.model)
        result = await self.session.execute(query)
        return [self.mapper.map_to_domain_entity(model) for model in result.scalars().all()]

    @notify_on_error
    async def get_one(self, **kwargs):
        query = select(self.model).filter_by(**kwargs)
        result = await self.session.execute(query)
        print(query.compile(compile_kwargs={"literal_binds": True}))
        try:
            model = result.scalars().one()
        except NoResultFound:
            raise ObjectNotFoundException
        return self.mapper.map_to_domain_entity(model)

    @notify_on_error
    async def get_one_or_none(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()
        if model:
            return self.mapper.map_to_domain_entity(model)
        return None

    @notify_on_error
    async def get_in_params(self, *args, **filter_by):
        query = select(self.model).filter(*args).filter_by(**filter_by)
        result = await self.session.execute(query)
        if result:
            return [self.mapper.map_to_domain_entity(model) for model in result.scalars().all()]
        return None

    @notify_on_error
    async def add(self, data: BaseModel):
        added_stm = insert(self.model).values(**data.model_dump()).returning(self.model)
        try:
            result = await self.session.execute(added_stm)
            model = result.scalars().one()
            return self.mapper.map_to_domain_entity(model)
        except IntegrityError as ex:
            logging.error(f"Failed to add data {data} due to {type(ex.orig.__cause__)=}")
            if isinstance(ex.orig.__cause__, UniqueViolationError):
                raise ObjectAlreadyExistsException from ex
            raise ex

    @notify_on_error
    async def add_bulk(self, data: list[BaseModel]):
        added_stm = insert(self.model).values([item.model_dump() for item in data])
        await self.session.execute(added_stm)

    @notify_on_error
    async def delete_bulk(self, data: list[BaseModel]):
        rows = [item.model_dump() for item in data]
        conditions = [and_(*[getattr(self.model, k) == v for k, v in row.items()]) for row in rows]

        if not conditions:
            return
        final_condition = conditions[0] if len(conditions) == 1 else or_(*conditions)

        delete_stm = delete(self.model).where(final_condition)
        print(delete_stm.compile(compile_kwargs={"literal_binds": True}))
        await self.session.execute(delete_stm)

    @notify_on_error
    async def update(self, data: BaseModel, exclude_unset: bool = False, **filter_by):
        update_stm = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**data.model_dump(exclude_unset=exclude_unset))
        )
        await self.session.execute(update_stm)

    @notify_on_error
    async def delete(self, **filter_by):
        delete_stm = delete(self.model).filter_by(**filter_by)
        await self.session.execute(delete_stm)
