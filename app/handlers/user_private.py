from aiogram import types, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import cart_crud, user_crud
from app.filters.chat_types import ChatTypeFilter
from app.keyboards.inline import MenuCallBack
from .menu_processing import get_menu_content


# Список разрешенных типов чатов.
CHAT_TYPES = [
    'private',
]

user_private_router = Router()
user_private_router.message.filter(
    ChatTypeFilter(CHAT_TYPES)
)


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message, session: AsyncSession):
    media, reply_markup = await get_menu_content(
        session=session,
        level=0,
        menu_name='main'
    )
    await message.answer_photo(
        photo=media.media,
        caption=media.caption,
        reply_markup=reply_markup
    )


async def add_to_cart(
        callback: CallbackQuery,
        callback_data: MenuCallBack,
        session: AsyncSession
):
    user = callback.from_user
    await user_crud.create(obj_in=dict(
        user_id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=None
    ), session=session)

    await cart_crud.add_to_cart(
        user_id=user.id,
        product_id=callback_data.product_id,
        session=session
    )


@user_private_router.callback_query(MenuCallBack.filter())
async def user_menu(
        callback: types.CallbackQuery,
        callback_data: MenuCallBack,
        session: AsyncSession
):
    if callback_data.menu_name == 'add_to_cart':
        await add_to_cart(callback, callback_data, session)
        await callback.answer('Товар в корзине')
        return
    media, reply_markup = await get_menu_content(
        session=session,
        level=callback_data.level,
        menu_name=callback_data.menu_name,
        category_id=callback_data.category_id,
        page=callback_data.page,
        user_id=callback.from_user.id,
        product_id=callback_data.product_id
    )

    await callback.message.edit_media(
        media=media,
        reply_markup=reply_markup
    )
    await callback.answer()
