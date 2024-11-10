from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import CRUDBase
from app.models import User


class CRUDUser(CRUDBase):

    async def get_by_telegram_user_id(
            self,
            user_id: int,
            session: AsyncSession,
    ):
        db_obj = await session.execute(
            select(self.model).where(
                self.model.user_id == user_id
            )
        )
        return db_obj.scalars().first()

    async def create(
            self,
            obj_in,
            session: AsyncSession,
    ):
        user = await self.get_by_telegram_user_id(
            user_id=int(obj_in['user_id']),
            session=session
        )
        if not user:
            return await super().create(obj_in=obj_in, session=session)
        return user


user_crud = CRUDUser(model=User)
