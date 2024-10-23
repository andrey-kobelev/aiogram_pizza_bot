from aiogram.types import BotCommand

from .constants import (
    MENU,
    ABOUT,
    PAYMENT,
    SHIPPING
)


PRIVATE = [
    BotCommand(command=MENU.command, description=MENU.description),
    BotCommand(command=ABOUT.command, description=ABOUT.description),
    BotCommand(command=PAYMENT.command, description=PAYMENT.description),
    BotCommand(command=SHIPPING.command, description=SHIPPING.description),
]
