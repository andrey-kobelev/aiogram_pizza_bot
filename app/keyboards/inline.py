from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


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
def get_inlineMix_btns(
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
