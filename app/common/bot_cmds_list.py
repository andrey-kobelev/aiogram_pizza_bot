from collections import namedtuple

from aiogram.types import BotCommand


button = namedtuple(
    typename='Button',
    field_names=[
        'command',
        'description'
    ]
)
MENU = button('menu', 'Меню')
ABOUT = button('about', 'О нас')
PAYMENT = button('payment', 'Варианты оплаты')
SHIPPING = button('shipping', 'Варианты доставки')

PRIVATE = [
    BotCommand(command=MENU.command, description=MENU.description),
    BotCommand(command=ABOUT.command, description=ABOUT.description),
    BotCommand(command=PAYMENT.command, description=PAYMENT.description),
    BotCommand(command=SHIPPING.command, description=SHIPPING.description),
]
