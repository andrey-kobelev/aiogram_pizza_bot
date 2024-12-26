from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove, KeyboardButtonPollType
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder


from app.common import constants as button


START_BUTTONS = [
    [
        KeyboardButton(text=button.CATALOG.text),
        KeyboardButton(text=button.ABOUT.text),
    ],
    [
        KeyboardButton(text=button.SHIPPING.text),
        KeyboardButton(text=button.PAYMENT.text),
    ]
]

start_kb = ReplyKeyboardMarkup(
    keyboard=[
        *START_BUTTONS
    ],
    resize_keyboard=True,
    input_field_placeholder=button.INPUT_TEXT
)

remove_start_kb = ReplyKeyboardRemove()

start_kb_2 = ReplyKeyboardBuilder()

start_kb_2.add(*(START_BUTTONS[0] + START_BUTTONS[1]))

start_kb_2.adjust(2, 2)

start_kb_3 = ReplyKeyboardBuilder()

start_kb_3.attach(start_kb_2)
start_kb_3.row(KeyboardButton(text=button.ABOUT.text))


contact_location_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text='Создать опрос',
                request_poll=KeyboardButtonPollType()
            ),
        ],
        [
            KeyboardButton(text='Отправить номер', request_contact=True),
            KeyboardButton(text='Отправить локацию', request_location=True),
        ]
    ],
    resize_keyboard=True
)


def get_keyboard(
        *buttons: str,
        placeholder: str = None,
        request_contact: int = None,
        request_location: int = None,
        sizes: tuple[int, ...] = (2,)
):
    """
    Parameters request_contact and request_location
    must be as indexes of buttons args for buttons you need.
    Example:
    get_keyboard(
            "Меню",
            "О магазине",
            "Варианты оплаты",
            "Варианты доставки",
            "Отправить номер телефона"
            placeholder="Что вас интересует?",
            request_contact=4,
            sizes=(2, 2, 1)
        )
    """
    keyboard = ReplyKeyboardBuilder()

    for index, text in enumerate(buttons, start=0):
        if request_contact and request_contact == index:
            keyboard.add(KeyboardButton(text=text, request_contact=True))
        elif request_location and request_location == index:
            keyboard.add(KeyboardButton(text=text, request_location=True))
        else:
            keyboard.add(KeyboardButton(text=text))

    return keyboard.adjust(*sizes).as_markup(
        resize_keyboard=True, input_field_placeholder=placeholder
    )
