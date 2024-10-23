from string import punctuation

from aiogram import types, Router, Bot
from aiogram.filters import Command

from app.filters.chat_types import ChatTypeFilter


# Список разрешенных типов чатов.
CHAT_TYPES = [
    'group',
    'supergroup',
]

RESTRICTED_WORDS = {
    'хрен',
    'грязь',
    'блин'
}

user_group_router = Router()
user_group_router.message.filter(
    ChatTypeFilter(CHAT_TYPES)
)


# Секретная команда
@user_group_router.message(Command('admin'))
async def get_admins(message: types.Message, bot: Bot):
    # Делаем запрос на сервер телеграмма
    admins = await bot.get_chat_administrators(message.chat.id)
    admins = [
        member.user.id
        for member in admins
        if member.status == 'creator' or member.status == 'administrator'
    ]
    bot.admins = admins
    # Можно удалить сразу сообщение, чтобы никто не увидел
    if message.from_user.id in admins:
        await message.delete()


def clean_text(text: str):
    return text.translate(str.maketrans('', '', punctuation))


# edited_message для того, чтобы отлавливать отредактированные сообщения.
@user_group_router.edited_message()
@user_group_router.message()
async def check_and_clean_bad_words(message: types.Message):
    if RESTRICTED_WORDS.intersection(
        clean_text(message.text.lower()).split()
    ):
        # Написать пользователю сообщение перед удалением
        await message.reply(
            f'{message.from_user.first_name}, соблюдайте порядок в чате!'
        )
        # Удалить сообщение.
        await message.delete()

        # Если нужно забанить пользователя
        # await message.chat.ban(message.from_user.id)
