from collections import namedtuple

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
REVIEW = button('review', 'Оставить отзыв')

INPUT_TEXT = 'Что Вас интересует?'
