import asyncio
import os

import dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommandScopeAllPrivateChats

from handlers import ROUTERS
from common import PRIVATE
from middlewares.db import DBSession
from core.db import AsyncSessionLocal
# from core.db import create_db


dotenv.load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')

ALLOWED_UPDATES = ['message', 'edited_message', 'callback_query']

# Класс самого бота - инициализация.
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
bot.admins = []

# Обрабатывает все апдейты из сервера - всё что касается бота.
# Отвечает за фильтрацию сообщений полученных с сервера.
# PS:
# В предыдущей версии нужно было передать объект бота.
dispatcher = Dispatcher()
dispatcher.include_routers(*ROUTERS)


async def on_startup_func(bot):
    # await create_db()
    print('Запустили бот')


async def on_shutdown_func(bot):
    print('Завершили бот')


async def main():
    dispatcher.startup.register(on_startup_func)
    dispatcher.shutdown.register(on_shutdown_func)

    dispatcher.update.middleware(DBSession(async_session=AsyncSessionLocal))

    # Перед запуском сбрасываем старые обновления и начнем пуллинг с новых.
    await bot.delete_webhook(drop_pending_updates=True)

    # Настройка уделения пункта меню для последующего пересоздания.
    # await bot.delete_my_commands(
    #     scope=BotCommandScopeAllPrivateChats()
    # )

    # Здесь прописана настройка отображения меню в приватных чатах.
    await bot.set_my_commands(
        commands=PRIVATE,
        scope=BotCommandScopeAllPrivateChats()
    )

    # Здесь бот начнет слушать сервер ТГ,
    # и спрашивать у него о наличии обновлений.
    await dispatcher.start_polling(
        bot,
        # allowed_updates=ALLOWED_UPDATES,
        # Что-бы не прописывать каждый тип апдейта.
        # Те апдейты которые мы используем -
        # автоматически будут передаваться сюда.
        allowed_updates=dispatcher.resolve_used_update_types()
    )


if __name__ == '__main__':
    asyncio.run(main())
