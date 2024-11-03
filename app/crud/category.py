from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import CRUDBase
from app.models import Category


class CRUDCategory(CRUDBase):

    async def create_categories(session: AsyncSession, categories: list):
        query = select(Category)
        result = await session.execute(query)
        if result.first():
            return
        session.add_all([Category(name=name) for name in categories])
        await session.commit()


category_crud = CRUDCategory(model=Category)
