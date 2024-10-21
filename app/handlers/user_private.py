from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command, or_f

from app.filters.chat_types import ChatTypeFilter


# Список разрешенных типов чатов.
CHAT_TYPES = [
    'private',
]

user_private_router = Router()
user_private_router.message.filter(
    ChatTypeFilter(CHAT_TYPES)
)


# С помощью готовой системы фильтрации хендлер
# будет реагировать на /start нужным образом.
@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer('Отвечаю на сообщение /start')


@user_private_router.message(or_f(Command('menu'), F.text.lower() == 'меню'))
async def menu_cmd(message: types.Message):
    await message.answer('Наше меню')

# ВАЖНА ПОСЛЕДОВАТЕЛЬНОСТЬ ФИЛЬТРАЦИИ СОБЫТИЙ!
# Если echo разместить перед start_cmd, то start_cmd никогда не выполнится!!!

# Хэндлер для обработки любого текстового
# сообщения (так как в скобках декоратора ничего не заданно),
# что бы бот отреагировал на него.
# Декоратор с типом события message - сообщение от пользователя.
# @user_private_router.message()
# async def echo(message: types.Message):
#     await message.answer(message.text)

    # Что-бы ответить с упоминанием автора.
    # await message.reply(message.text)


@user_private_router.message(
    (F.text.lower().contains('достав')) |
    (F.text.lower().contains('варианты доставки'))
)
@user_private_router.message(Command('shipping'))
async def shipping_cmd(message: types.Message):
    await message.answer('Варианты доставки')


@user_private_router.message(F.text.lower() == 'о нас')
@user_private_router.message(Command('about'))
async def about_cmd(message: types.Message):
    await message.answer('О нас')


@user_private_router.message(F.text.lower() == 'варианты оплаты')
@user_private_router.message(Command('payment'))
async def payment_cmd(message: types.Message):
    await message.answer('Варианты оплаты')
