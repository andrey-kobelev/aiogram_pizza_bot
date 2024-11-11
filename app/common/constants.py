from collections import namedtuple


text_menu_name_level = namedtuple(
    typename='InlineButtonData',
    field_names=[
        'text',
        'menu_name',
        'level'
    ]
)

MAIN_LEVEL = 0
CATALOG_LEVEL = 1
PRODUCTS_LEVEL = 2
CART_LEVEL = 3

MAIN_ = 'main'
BACK_ = 'Назад'
CATALOG_ = 'catalog'

CATALOG = text_menu_name_level("Товары 🍕", CATALOG_, CATALOG_LEVEL)
CART = text_menu_name_level("Корзина 🛒", "cart", CART_LEVEL)
ABOUT = text_menu_name_level("О нас ℹ️", "about", MAIN_LEVEL)
PAYMENT = text_menu_name_level("Оплата 💰", "payment", MAIN_LEVEL)
SHIPPING = text_menu_name_level("Доставка ⛵", "shipping", MAIN_LEVEL)

BACK_TO_MAIN_FROM_CATALOG = text_menu_name_level(BACK_, MAIN_, MAIN_LEVEL)
BACK_TO_CATALOG_FROM_PRODUCTS = text_menu_name_level(
    BACK_, CATALOG_, CATALOG_LEVEL
)
BACK_TO_MAIN = text_menu_name_level('На главную 🏠', MAIN_, MAIN_LEVEL)

ADD_TO_CART = text_menu_name_level('Купить 💵', 'add_to_cart', PRODUCTS_LEVEL)

INPUT_TEXT = 'Что Вас интересует?'
