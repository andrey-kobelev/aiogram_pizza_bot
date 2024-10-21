import asyncio
import os

import dotenv

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommandScopeAllPrivateChats

from handlers import ROUTERS
from common import PRIVATE


dotenv.load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
ALLOWED_UPDATES = ['message', 'edited_message']

# Класс самого бота - инициализация.
bot = Bot(token=TOKEN)

# Обрабатывает все апдейты из сервера - всё что касается бота.
# Отвечает за фильтрацию сообщений полученных с сервера.
# PS:
# В предыдущей версии нужно было передать объект бота.
dispatcher = Dispatcher()
dispatcher.include_routers(*ROUTERS)


async def main():
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
        allowed_updates=ALLOWED_UPDATES
    )


if __name__ == '__main__':
    asyncio.run(main())
