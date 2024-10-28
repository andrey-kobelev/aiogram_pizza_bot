from typing import Dict, Any

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession


class CRUDBase:

    def __init__(self, model):
        self.model = model

    async def get(
            self,
            obj_id: int,
            session: AsyncSession,
    ):
        db_obj = await session.execute(
            select(self.model).where(
                self.model.id == obj_id
            )
        )
        return db_obj.scalars().first()

    async def get_multi(
            self,
            session: AsyncSession
    ):
        db_objs = await session.execute(select(self.model))
        return db_objs.scalars().all()

    async def create(
            self,
            obj_in,
            session: AsyncSession,
    ):
        db_obj = self.model(**obj_in)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(
            self,
            obj_id: int,
            data: Dict[str, Any],
            session: AsyncSession,
    ):
        query = update(self.model).where(self.model.id == obj_id).values(
            **data
        )
        await session.execute(query)
        await session.commit()

    async def remove(
            self,
            obj_id: int,
            session: AsyncSession,
    ):
        query = delete(self.model).where(self.model.id == obj_id)
        await session.execute(query)
        await session.commit()
