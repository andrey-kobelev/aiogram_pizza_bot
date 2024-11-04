from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import CRUDBase
from app.models.category import Category


class CRUDCategory(CRUDBase):

    async def create_categories(self, session: AsyncSession, categories: list):
        query = select(self.model)
        result = await session.execute(query)
        if result.first():
            return
        session.add_all([self.model(name=name) for name in categories])
        await session.commit()


category_crud = CRUDCategory(model=Category)
