from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command, or_f
from aiogram.utils.formatting import as_list, as_marked_section, Bold
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.product import product_crud
from app.filters.chat_types import ChatTypeFilter
from app.keyboards import reply
from app.common import constants as cmd


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
    await message.answer(
        text='Отвечаю на сообщение /start',
        # Вторым параметром можно передать клавиатуру.
        # reply_markup=reply.start_kb
        # ____________________________
        # Второй вид клавиатуры передается по другому
        reply_markup=reply.start_kb_3.as_markup(
            resize_keyboard=True,
            input_field_placeholder=cmd.INPUT_TEXT
        )
    )


@user_private_router.message(
    or_f(
        Command(cmd.MENU.command),
        F.text.lower() == 'меню'
    )
)
async def menu_cmd(message: types.Message, session: AsyncSession):
    products = await product_crud.get_multi(session=session)
    # products = '\n'.join([
    #     f'ID: {product.id}\n'
    #     f'Название: {product.name}\n'
    #     f'Описание: {product.description}\n'
    #     for product in products
    # ])
    for product in products:
        await message.answer_photo(
            product.image,
            caption=(
                f'<strong>{product.name}</strong>\n'
                f'{product.description}\n'
                f'Стоимость: {round(product.price, 2)}'
            )
        )
    await message.answer(
        text='Наше меню',
        # При переходе к меню удалить клавиатуру.
        reply_markup=reply.remove_start_kb
    )

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
@user_private_router.message(Command(cmd.SHIPPING.command))
async def shipping_cmd(message: types.Message):
    shipping_options = [
        'Курьер',
        'Самовывоз',
        'Покушаю у вас',
    ]
    forbidden = [
        'Почта', 'Голуби',
    ]
    # Список маркированных объектов с разделителем sep.
    text = as_list(
        as_marked_section(
            Bold(f'{cmd.SHIPPING.description}:'),
            *shipping_options,
            marker='* '
        ),
        as_marked_section(
            Bold('Нельзя:'),
            *forbidden,
            marker='X '
        ),
        sep='\n__________________\n'
    )
    await message.answer(
        text=text.as_html(),
    )


@user_private_router.message(F.text.lower() == 'о нас')
@user_private_router.message(Command(cmd.ABOUT.command))
async def about_cmd(message: types.Message):
    await message.answer(
        text='О нас',
        reply_markup=reply.contact_location_kb
    )


@user_private_router.message(F.text.lower() == 'варианты оплаты')
@user_private_router.message(Command(cmd.PAYMENT.command))
async def payment_cmd(message: types.Message):
    payment_options = [
        'Картой в боте',
        'При получении карта/кеш',
        'В заведении'
    ]

    # Вернется класс текста
    text = as_marked_section(
        # Title. Текст сделается жирным
        Bold(f'{cmd.PAYMENT.description}:'),
        # Body
        *payment_options,
        marker='* '
    )
    # Нужно указать как именно мы будем парсить текст.
    await message.answer(text.as_html())


@user_private_router.message(F.contact)
async def get_contact(message: types.Message):
    await message.answer('Номер получен')
    await message.answer(str(message.contact.phone_number))


@user_private_router.message(F.location)
async def get_location(message: types.Message):
    await message.answer('Локация получена')
    await message.answer(str(message.location))
