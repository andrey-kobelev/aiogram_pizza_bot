from typing import Optional

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.common import constants as consts
from app.utils.paginator import Paginator


class MenuCallBack(CallbackData, prefix='menu'):
    level: int
    menu_name: Optional[str] = None
    category_id: Optional[int] = None
    page: int = 1
    product_id: Optional[int] = None
    # Передается вручную. Это требуется для стандартизации
    # приема аргументов функцией
    # (смотреть в user_private.start_cmd).
    user_id: Optional[int] = None


def get_next_and_previous_buttons_row(
        paginator: Paginator,
        page: int,
        **kwargs
) -> list[InlineKeyboardButton]:
    previous = (
        ('◀ Пред.', 'previous', page - 1)
        if paginator.has_previous() else None
    )
    next_ = (
        ('След. ▶', 'next', page + 1)
        if paginator.has_next() else None
    )
    return [
        InlineKeyboardButton(
            text=text,
            callback_data=MenuCallBack(
                level=kwargs['level'],
                menu_name=menu_name,
                category_id=kwargs.get('category_id', None),
                page=page_
            ).pack()
        )
        for text, menu_name, page_ in (
            tuple(action for action in (previous, next_) if action)
        )
    ]


def get_main_keyboard(
        *,
        sizes: tuple[int] = (2,)
):
    keyboard = InlineKeyboardBuilder()
    for button_data in (
        consts.CATALOG,
        consts.CART,
        consts.ABOUT,
        consts.PAYMENT,
        consts.SHIPPING
    ):
        keyboard.add(InlineKeyboardButton(
            text=button_data.text,
            callback_data=MenuCallBack(
                level=button_data.level,
                menu_name=button_data.menu_name
            ).pack()
        ))
    return keyboard.adjust(*sizes).as_markup()


def get_catalog_keyboard(
        *,
        categories: list,
        sizes: tuple[int] = (2,)
):
    keyboard = InlineKeyboardBuilder()

    for button_data in (
        consts.BACK_TO_MAIN_FROM_CATALOG,
        consts.CART
    ):
        keyboard.add(InlineKeyboardButton(
            text=button_data.text,
            callback_data=MenuCallBack(
                level=button_data.level,
                menu_name=button_data.menu_name
            ).pack()
        ))

    for category in categories:
        keyboard.add(InlineKeyboardButton(
            text=category.name,
            callback_data=MenuCallBack(
                level=consts.PRODUCTS_LEVEL,
                category_id=category.id
            ).pack()
        ))

    return keyboard.adjust(*sizes).as_markup()


def get_products_keyboard(
        *,
        level: int,
        category_id: int,
        page: int,
        product_id: int,
        sizes: tuple[int] = (2, 1),
        paginator: Paginator
):
    keyboard = InlineKeyboardBuilder()

    for button_data in (
        consts.BACK_TO_CATALOG_FROM_PRODUCTS,
        consts.CART,
        consts.ADD_TO_CART
    ):
        keyboard.add(InlineKeyboardButton(
            text=button_data.text,
            callback_data=MenuCallBack(
                level=button_data.level,
                menu_name=button_data.menu_name,
                product_id=product_id
            ).pack()
        ))

    keyboard.adjust(*sizes)

    return keyboard.row(*get_next_and_previous_buttons_row(
        paginator=paginator,
        page=page,
        level=level,
        category_id=category_id
    )).as_markup()


def get_user_cart_keyboard(
        *,
        level: int,
        page: Optional[int],
        product_id: Optional[int],
        sizes: tuple[int] = (3,),
        paginator: Optional[Paginator] = None
):
    keyboard = InlineKeyboardBuilder()
    if page:
        keyboard.add(InlineKeyboardButton(
            text='Удалить',
            callback_data=MenuCallBack(
                level=level,
                menu_name='delete',
                product_id=product_id,
                page=page
            ).pack()
        ))
        keyboard.add(InlineKeyboardButton(
            text='-1',
            callback_data=MenuCallBack(
                level=level,
                menu_name='decrement',
                product_id=product_id,
                page=page
            ).pack()
        ))
        keyboard.add(InlineKeyboardButton(
            text='+1',
            callback_data=MenuCallBack(
                level=level,
                menu_name='increment',
                product_id=product_id,
                page=page
            ).pack()
        ))

        keyboard.adjust(*sizes)

        if paginator:
            keyboard.row(*get_next_and_previous_buttons_row(
                paginator=paginator,
                page=page,
                level=level
            ))

        row2 = [
            InlineKeyboardButton(
                text='На главную 🏠',
                callback_data=MenuCallBack(level=0, menu_name='main').pack()
            ),
            InlineKeyboardButton(
                text='Заказать',
                callback_data=MenuCallBack(level=0, menu_name='order').pack()
            ),
        ]
        return keyboard.row(*row2).as_markup()
    else:
        keyboard.add(
            InlineKeyboardButton(
                text='На главную 🏠',
                callback_data=MenuCallBack(level=0, menu_name='main').pack()
            )
        )

        return keyboard.adjust(*sizes).as_markup()


def get_callback_btns(
        # * - автоматический запрет на передачу неименованных аргументов.
        *,
        # В словаре будет указываться text как ключ,
        # а в value - строка с данными, которые отправятся боту.
        btns: dict[str, str],
        sizes: tuple[int] = (2,)
):
    keyboard = InlineKeyboardBuilder()
    # Проходимся по словарю
    for text, data in btns.items():
        # Reply-кнопки отправляют только то,
        # что на них написано в чат, а inline нет.
        # Тут создаем именно кнопку.
        # Параметр text - только для отображения,
        # а в callback_data передаются данные,
        # которые бот сможет как то обработать
        # хендлером отлавливающим CallbackQuery-события.
        # PS: callback_data не отправляется в чат,
        # то есть эти данные невидимы для пользователя.
        # PPS: Вместо callback_data можно отправить url -
        # тогда произойдет типа редиректа.
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()


# Если понадобятся кнопки с URL
def get_url_btns(
        *,
        btns: dict[str, str],
        sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    for text, url in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, url=url))

    return keyboard.adjust(*sizes).as_markup()


# Создать микс из CallBack и URL кнопок
def get_inline_mix_btns(
        *,
        btns: dict[str, str],
        sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    for text, value in btns.items():
        if '://' in value:
            keyboard.add(InlineKeyboardButton(text=text, url=value))
        else:
            keyboard.add(InlineKeyboardButton(text=text, callback_data=value))

    return keyboard.adjust(*sizes).as_markup()
