from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import CRUDBase
from app.models import Banner


class CRUDBanner(CRUDBase):

    async def create_multiple(
            self,
            obj_in: dict,
            session: AsyncSession,
    ):
        # Добавляем новый или изменяем существующий по именам
        # пунктов меню: main, about, cart, shipping, payment, catalog
        query = select(self.model)
        result = await session.execute(query)
        if result.first():
            return
        session.add_all([
            self.model(name=name, description=description)
            for name, description in obj_in.items()
        ])
        await session.commit()


banner_crud = CRUDBanner(model=Banner)
