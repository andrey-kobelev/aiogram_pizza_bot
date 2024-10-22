from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from app.common import bot_cmds_list as button


INPUT_TEXT = 'Что Вас интересует?'

START_BUTTONS = [
    [
        KeyboardButton(text=button.MENU.description),
        KeyboardButton(text=button.ABOUT.description),
    ],
    [
        KeyboardButton(text=button.SHIPPING.description),
        KeyboardButton(text=button.PAYMENT.description),
    ]
]

start_kb = ReplyKeyboardMarkup(
    keyboard=[
        *START_BUTTONS
    ],
    resize_keyboard=True,
    input_field_placeholder=INPUT_TEXT
)
