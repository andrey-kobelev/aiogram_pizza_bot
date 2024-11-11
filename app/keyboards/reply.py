from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove, KeyboardButtonPollType
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder


from app.common import constants as button


# Каждый список из KeyboardButton - это строка (ряд) из кнопок.
# Если судить по такой конструкции, то получится две строки по две кнопки.
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
        # Распаковать список с кнопками в список.
        *START_BUTTONS
    ],
    # Что-бы кнопки не были огромными
    resize_keyboard=True,
    # Поменять строку приглашения к вводу сообщения на кастомную.
    input_field_placeholder=button.INPUT_TEXT
)

# Если нужно удалить клавиатуру,
# то применить данный объект в нужном хендлере.
remove_start_kb = ReplyKeyboardRemove()

# Создаем экземпляр
start_kb_2 = ReplyKeyboardBuilder()

# Теперь передает кнопки с помощью методов.
start_kb_2.add(*(START_BUTTONS[0] + START_BUTTONS[1]))

# Теперь можно цифрами расписать сколько
# строк по сколько столбцов отображать кнопки.
# Каждая цифра - это ряд (1-я: 1 ряд 2 кнопки; 2-я: 2 ряд 2 кнопки).
start_kb_2.adjust(2, 2)

# Добавить еще клавиатуру на основе предыдущей, но с добавлением новой кнопки.
start_kb_3 = ReplyKeyboardBuilder()

# Наследуемся как бы от другой клавиатуры
start_kb_3.attach(start_kb_2)
# Добавляем новую кнопку
# start_kb_3.add(KeyboardButton(text=button.REVIEW.description))

# Метод row добавит кнопку новым рядом.
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


# Удобно будет видеть в хендлерах какими кнопками его клавиатура располагает.
def get_keyboard(
        *buttons: str,
        placeholder: str = None,
        # Передается индекс кнопки к которой нужно
        # прицепить передачу контакта или локации.
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
