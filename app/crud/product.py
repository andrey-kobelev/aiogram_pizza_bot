from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Product
from app.crud.base import CRUDBase


class CRUDProduct(CRUDBase):

    async def get_multi(
            self,
            session: AsyncSession,
            category_id: int = None,
    ):
        if category_id:
            db_objs = await session.execute(select(self.model).where(
                self.model.category_id == category_id
            ))
            return db_objs.scalars().all()
        return await super().get_multi(session=session)


product_crud = CRUDProduct(model=Product)
