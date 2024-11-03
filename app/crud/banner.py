from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .base import CRUDBase
from app.models import Banner


class CRUDBanner(CRUDBase):

    async def create(
            self,
            obj_in,
            session: AsyncSession,
    ):
        # Добавляем новый или изменяем существующий по именам
        # пунктов меню: main, about, cart, shipping, payment, catalog
        query = select(self.model)
        result = await session.execute(query)
        if result.first():
            return
        session.add(self.model(**obj_in))
        await session.commit()

    async def update(
            self,
            *,
            name: str,
            image: str,
            session: AsyncSession,
    ):
        query = update(self.model).where(
            self.model.name == name
        ).values(image=image)
        await session.execute(query)
        await session.commit()


banner_crud = CRUDBanner(model=Banner)
