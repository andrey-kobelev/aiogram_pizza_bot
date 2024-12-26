from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.crud import user_crud


class DBSession(BaseMiddleware):
    def __init__(self, async_session: async_sessionmaker):
        self.async_session = async_session

    async def __call__(
            self,
            handler: Callable[
                [TelegramObject, Dict[str, Any]],
                Awaitable[Any]
            ],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        async with self.async_session() as session:
            data['session'] = session
            return await handler(event, data)


class CreateUserMiddleware(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[
                [TelegramObject, Dict[str, Any]],
                Awaitable[Any]
            ],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        user = event.from_user
        db_user = await user_crud.create(obj_in=dict(
            user_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=None
        ), session=data['session'])
        data['db_user'] = db_user
        return await handler(event, data)
