from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from app.filters.chat_types import ChatTypeFilter, IsAdmin
from app.keyboards.reply import get_keyboard


admin_router = Router()
admin_router.message.filter(ChatTypeFilter(['private']), IsAdmin())

ADMIN_BUTTONS = [
    'Добавить товар',
    'Изменить товар',
    'Удалить товар',
    'Я так, просто посмотреть зашел',
]
BACK_CANCEL_BUTTONS = [
    'назад',
    'отмена',
]

ADMIN_KB = get_keyboard(
    *ADMIN_BUTTONS,
    placeholder='Выберите действие',
    sizes=(2, 1, 1),
)
BACK_CANCEL_KB = get_keyboard(
    *BACK_CANCEL_BUTTONS,
    placeholder='Введите данные о товаре',
)


@admin_router.message(Command('admin'))
async def add_product(message: types.Message):
    await message.answer(
        text='Что хотите сделать?',
        reply_markup=ADMIN_KB
    )


@admin_router.message(F.text == 'Я так, просто посмотреть зашел')
async def starring_at_product(message: types.Message):
    await message.answer('ОК, вот список товаров')


@admin_router.message(F.text == 'Изменить товар')
async def change_product(message: types.Message):
    await message.answer('ОК, вот список товаров')


@admin_router.message(F.text == 'Удалить товар')
async def delete_product(message: types.Message):
    await message.answer('Выберите товар(ы) для удаления')


# КОД НИЖЕ ДЛЯ МАШИНЫ СОСТОЯНИЙ (FSM)
class AddProduct(StatesGroup):
    # Каждый пункт это состояние на котором
    # может находиться каждый пользователь (?).
    name = State()
    description = State()
    price = State()
    image = State()

    texts = {
        'AddProduct:name': 'Введите название заново:',
        'AddProduct:description': 'Введите описание заново:',
        'AddProduct:price': 'Введите стоимость заново:',
        'AddProduct:image': 'Этот стейт последний, поэтому...',
    }


# 1) FSM начнется, если у пользователя
# нет активных состояний - StateFilter(None).
# Это точка входа в состояние.
@admin_router.message(StateFilter(None), F.text == 'Добавить товар')
async def add_product_fsm(message: types.Message, state: FSMContext):
    await message.answer(
        text='Введите название товара',
        reply_markup=BACK_CANCEL_KB
    )
    # Нужно указать в какое состояние нужно стать
    await state.set_state(AddProduct.name)


# Сбросить состояние пользователя.
# '*' - обозначает любое состояние пользователя.
@admin_router.message(StateFilter('*'), Command('отмена'))
@admin_router.message(StateFilter('*'), F.text.casefold() == 'отмена')
async def cancel(message: types.Message, state: FSMContext) -> None:
    # Сохраним текущее состояние в переменную.
    current_state = state.get_state()
    # Если у пользователя нет никакого состояния ..
    if current_state is None:
        # Завершаем работу хендлера.
        return
    # В ином случае очищаем данные и убираем все состояния.
    await state.clear()
    await message.answer(
        text='Все действия отменены',
        reply_markup=ADMIN_KB
    )


@admin_router.message(StateFilter('*'), Command('назад'))
@admin_router.message(StateFilter('*'), F.text.casefold() == 'назад')
async def back(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state == AddProduct.name:
        await message.answer(
            'Предыдущего шага нет, '
            'или введите название товара или нажмите "отмена"'
        )
        return
    previous = None
    for step in AddProduct.__all_states__:
        if step.state == current_state:
            print(f'{previous=} {current_state=} {step=} {step.state=}')
            await state.set_state(previous)
            await message.answer(
                'Вы вернулись к прошлому шагу '
                f'\n {AddProduct.texts[previous.state]}'
            )
            return
        previous = step


# 2) Если пользователь в состоянии AddProduct.name и ввел текст,
# то продолжаем FSM
@admin_router.message(AddProduct.name, F.text)
async def add_name(message: types.Message, state: FSMContext):
    # Записываем name из предыдущего шага
    await state.update_data(name=message.text)
    await message.answer(
        text='Введите описание товара'
    )
    # Меняем состояние на description
    await state.set_state(AddProduct.description)


# Если вместо текста будет другое событие,
# то выполнится этот хендлер, но состояние останется прежним.
@admin_router.message(AddProduct.name)
async def fix_name(message: types.Message):
    await message.reply(
        text=(
            'Название товара было введено некорректно, '
            'введите название еще раз'
        )
    )


# 3) Если пользователь в состоянии AddProduct.description и ввел текст,
# то продолжаем FSM
@admin_router.message(AddProduct.description, F.text)
async def add_description(message: types.Message, state: FSMContext):
    # Записываем description
    await state.update_data(description=message.text)
    await message.answer(
        text='Введите стоимость товара'
    )
    # Меняем состояние на price
    await state.set_state(AddProduct.price)


@admin_router.message(AddProduct.description)
async def fix_description(message: types.Message):
    await message.reply(
        text=(
            'Описание товара было введено некорректно, '
            'введите описание еще раз'
        )
    )


# 4) Если пользователь в состоянии AddProduct.price и ввел текст,
# то продолжаем FSM
@admin_router.message(AddProduct.price, F.text)
async def add_price(message: types.Message, state: FSMContext):
    # Записываем price
    await state.update_data(price=message.text)
    await message.answer(
        text='Загрузите изображение товара'
    )
    # Меняем состояние на image
    await state.set_state(AddProduct.image)


@admin_router.message(AddProduct.price)
async def fix_price(message: types.Message):
    await message.reply(
        text=(
            'Цена товара была введена некорректно, '
            'введите цену еще раз'
        )
    )


# 5) Если пользователь в состоянии AddProduct.image и загрузил фото,
# то продолжаем FSM
@admin_router.message(AddProduct.image, F.photo)
async def add_image(message: types.Message, state: FSMContext):
    # Записываем в словарь фото.
    # photo[-1] - означает самое высокое качество,
    # так как на серверах хранится несколько вариантов фото.
    # К каждому изображению ТГ присваивает уникальные id
    await state.update_data(image=message.photo[-1].file_id)
    await message.answer(
        text='Товар добавлен',
        reply_markup=ADMIN_KB
    )
    # Теперь полученные данные можно куда-нибудь сохранить.
    data = await state.get_data()
    await message.answer(str(data))
    # Когда пользователь прошел все пункты -
    # очистить состояние пользователя и удалить все данные из машины состояния!
    await state.clear()


@admin_router.message(AddProduct.image)
async def fix_image(message: types.Message):
    await message.reply(
        text=(
            'Некорректный тип изображения, '
            'попробуйте загрузить другое'
        )
    )
