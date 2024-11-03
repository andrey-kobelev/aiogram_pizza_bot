from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import CRUDBase
from app.models import User


class CRUDUser(CRUDBase):

    async def create(
            self,
            obj_in,
            session: AsyncSession,
    ):
        query = select(self.model).where(
            self.model.user_id == obj_in['user_id']
        )
        result = await session.execute(query)
        if result.first() is None:
            await super().create(obj_in=obj_in, session=session)


user_crud = CRUDUser(model=User)
