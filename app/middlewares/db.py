from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker


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


# class CounterMiddleware(BaseMiddleware):
#     def __init__(self) -> None:
#         self.counter = 0
#
#     async def __call__(
#         self,
#         # Автоматически пробрасывается экземпляр хендлера
#         handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
#         # Какое было событие? Message, CallbackQuery ...
#         event: TelegramObject,
#         # data - Специальный словарь, который в себе собирает все,
#         # что может передаваться в хендлер -
#         # промежуточные слои (state, session (скоро), и так далее)
#         data: Dict[str, Any]
#     ) -> Any:
#         self.counter += 1
#         data['counter'] = self.counter
#         return await handler(event, data)
