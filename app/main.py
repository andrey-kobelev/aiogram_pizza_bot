import asyncio
import os

import dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from app.middlewares.db import CreateUserMiddleware
from app.handlers import ROUTERS
from app.middlewares.db import DBSession
from app.core.db import AsyncSessionLocal, import_data


dotenv.load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')

ALLOWED_UPDATES = ['message', 'edited_message', 'callback_query']

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
bot.admins = []

dispatcher = Dispatcher()
dispatcher.include_routers(*ROUTERS)


async def on_startup_func(bot: Bot):
    print('Datas are importing..')
    await import_data()
    print('Datas were imported.')
    print('Запустили бот')


async def on_shutdown_func(bot: Bot):
    print('Завершили бот')


async def main():
    dispatcher.startup.register(on_startup_func)
    dispatcher.shutdown.register(on_shutdown_func)

    dispatcher.update.middleware(DBSession(async_session=AsyncSessionLocal))
    dispatcher.message.middleware(CreateUserMiddleware())
    dispatcher.callback_query.middleware(CreateUserMiddleware())

    await bot.delete_webhook(drop_pending_updates=True)
    await dispatcher.start_polling(
        bot,
        allowed_updates=dispatcher.resolve_used_update_types()
    )


asyncio.run(main())
