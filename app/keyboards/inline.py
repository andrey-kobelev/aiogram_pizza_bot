from typing import Optional

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class MenuCallBack(CallbackData, prefix='menu'):
    level: int
    menu_name: str
    category_id: Optional[int] = None
    page: int = 1
    product_id: Optional[int] = None
    user_id: Optional[int] = None


def get_main_keyboard(*, level: int, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    buttons = {
        "Товары 🍕": "catalog",
        "Корзина 🛒": "cart",
        "О нас ℹ️": "about",
        "Оплата 💰": "payment",
        "Доставка ⛵": "shipping",
    }
    for text, menu_name in buttons.items():
        if menu_name == 'catalog':
            keyboard.add(InlineKeyboardButton(
                text=text,
                callback_data=MenuCallBack(
                    level=level + 1,
                    menu_name=menu_name
                ).pack()
            ))
        elif menu_name == 'cart':
            keyboard.add(InlineKeyboardButton(
                text=text,
                callback_data=MenuCallBack(level=3, menu_name=menu_name).pack()
            ))
        else:
            keyboard.add(InlineKeyboardButton(
                text=text,
                callback_data=MenuCallBack(
                    level=level,
                    menu_name=menu_name
                ).pack()
            ))

    return keyboard.adjust(*sizes).as_markup()


def get_catalog_keyboard(

        *,
        level: int,
        categories: list,
        sizes: tuple[int] = (2,)
):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(
        text='Назад',
        callback_data=MenuCallBack(level=level - 1, menu_name='main').pack()
    ))
    keyboard.add(InlineKeyboardButton(
        text='Корзина 🛒',
        callback_data=MenuCallBack(level=3, menu_name='cart').pack()
    ))

    for category in categories:
        keyboard.add(InlineKeyboardButton(
            text=category.name,
            callback_data=MenuCallBack(
                level=level + 1,
                menu_name=category.name,
                category_id=category.id
            ).pack()
        ))

    return keyboard.adjust(*sizes).as_markup()


def get_products_keyboard(
        *,
        level: int,
        category_id: int,
        page: int,
        next_previous_buttons: dict,
        product_id: int,
        sizes: tuple[int] = (2, 1)
):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(
        text='Назад',
        callback_data=MenuCallBack(level=level - 1, menu_name='catalog').pack()
    ))
    keyboard.add(InlineKeyboardButton(
        text='Корзина 🛒',
        callback_data=MenuCallBack(level=3, menu_name='cart').pack()
    ))
    keyboard.add(InlineKeyboardButton(
        text='Купить 💵',
        callback_data=MenuCallBack(
            level=level,
            menu_name='add_to_cart',
            product_id=product_id
        ).pack()
    ))

    keyboard.adjust(*sizes)

    row = []
    for text, menu_name in next_previous_buttons.items():
        if menu_name == "next":
            row.append(InlineKeyboardButton(
                text=text,
                callback_data=MenuCallBack(
                    level=level,
                    menu_name=menu_name,
                    category_id=category_id,
                    page=page + 1).pack()
            ))

        elif menu_name == "previous":
            row.append(InlineKeyboardButton(
                text=text,
                callback_data=MenuCallBack(
                    level=level,
                    menu_name=menu_name,
                    category_id=category_id,
                    page=page - 1).pack()
            ))

    return keyboard.row(*row).as_markup()


def get_user_cart(
        *,
        level: int,
        page: Optional[int],
        pagination_btns: Optional[dict],
        product_id: Optional[int],
        sizes: tuple[int] = (3,)
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

        row = []
        for text, menu_name in pagination_btns.items():
            if menu_name == "next":
                row.append(InlineKeyboardButton(
                    text=text,
                    callback_data=MenuCallBack(
                        level=level,
                        menu_name=menu_name,
                        page=page + 1
                    ).pack()
                ))
            elif menu_name == "previous":
                row.append(InlineKeyboardButton(
                    text=text,
                    callback_data=MenuCallBack(
                        level=level,
                        menu_name=menu_name,
                        page=page - 1
                    ).pack()
                ))

        keyboard.row(*row)

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
