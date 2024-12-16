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
    data = MenuCallBack(level=0, menu_name='main')
    media, reply_markup = await get_menu_content(
        session=session,
        data=data
    )
    await message.answer_photo(
        photo=media.media,
        caption=media.caption,
        reply_markup=reply_markup
    )


@user_private_router.callback_query(MenuCallBack.filter())
async def user_menu(
        callback: CallbackQuery,
        callback_data: MenuCallBack,
        session: AsyncSession,
):
    callback_data.user_id = callback.from_user.id
    db_user = await user_crud.get_by_telegram_user_id(
        user_id=callback.from_user.id,
        session=session
    )
    if callback_data.menu_name == 'order':
        await callback.answer(text='Товар Заказан!', show_alert=True)
        return
    if callback_data.menu_name == 'add_to_cart':
        await cart_crud.add_to_cart(
            user_id=db_user.user_id,
            product_id=callback_data.product_id,
            session=session
        )
        await callback.answer('Товар в корзине')
        return
    media, reply_markup = await get_menu_content(
        session=session,
        data=callback_data
    )

    await callback.message.edit_media(
        media=media,
        reply_markup=reply_markup
    )
    await callback.answer()
