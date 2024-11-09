from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy.ext.asyncio import AsyncSession

from app.filters.chat_types import ChatTypeFilter, IsAdmin
from app.keyboards.inline import get_callback_btns
from app.keyboards.reply import get_keyboard
from app.crud import product_crud, category_crud, banner_crud


admin_router = Router()
admin_router.message.filter(ChatTypeFilter(['private']), IsAdmin())

MANAGEMENT_BUTTONS = [
    'назад',
    'отмена',
    'пропустить'
]

ADMIN_KB = get_keyboard(
    "Добавить товар",
    "Ассортимент",
    "Добавить/Изменить баннер",
    placeholder="Выберите действие",
    sizes=(2,),
)
FSM_MANAGEMENT_KB = get_keyboard(
    *MANAGEMENT_BUTTONS,
    placeholder='Введите данные о товаре',
    sizes=(2, 1)
)
CANCEL_FSM_BANNER = get_keyboard(
    'отмена',
)


class AddProduct(StatesGroup):
    # Каждый пункт это состояние на котором
    # может находиться каждый пользователь (?).
    name = State()
    description = State()
    category = State()
    price = State()
    image = State()

    change_product_id = None

    texts = {
        'AddProduct:name': 'Введите название заново:',
        'AddProduct:description': 'Введите описание заново:',
        'AddProduct:price': 'Введите стоимость заново:',
        'AddProduct:image': 'Этот стейт последний, поэтому...',
    }


@admin_router.message(Command('admin'))
async def admin_zone(message: types.Message):
    await message.answer(
        text='Что хотите сделать?',
        reply_markup=ADMIN_KB
    )


@admin_router.message(F.text == 'Ассортимент')
async def get_products_list(message: types.Message, session: AsyncSession):
    categories = await category_crud.get_multi(session=session)
    btns = get_callback_btns(
        btns={
            category.name: f'category_{category.id}'
            for category in categories
        }
    )
    await message.answer("Выберите категорию", reply_markup=btns)


@admin_router.callback_query(F.data.startswith('category_'))
async def get_products_of_some_category(
        callback: types.CallbackQuery,
        session: AsyncSession
):
    category_id = int(callback.data.split('_')[1])
    products = await product_crud.get_multi(
        session=session,
        category_id=category_id
    )
    for product in products:
        await callback.message.answer_photo(
            product.image,
            caption=(
                f'<strong>{product.name}</strong>\n'
                f'{product.description}\n'
                f'Стоимость: {round(product.price, 2)}'
            ),
            reply_markup=get_callback_btns(
                btns={
                    # Передаем айди каждого продукта,
                    # потом, в другом хендлере (с событием CallbackQuery)
                    # нужно будет распарсить айди.
                    'Удалить': f'delete_{product.id}',
                    'Изменить': f'change_{product.id}',
                }
            )
        )
    await callback.answer()
    await callback.message.answer('ОК, вот список товаров: ⏫')


@admin_router.callback_query(F.data.startswith('delete_'))
async def delete_product(
        callback: types.CallbackQuery,
        session: AsyncSession
):
    product_id = int(callback.data.split('_')[-1])
    await product_crud.remove(obj_id=product_id, session=session)

    # Данная конструкция нужна для того,
    # что-бы по центру отобразился полупрозрачный
    # всплывающий текст "Товар удален".
    # Нужно указывать ОБЯЗАТЕЛЬНО, так как нужно
    # серверу дать сигнал о том, что мы приняли callback_query!
    # PS: Скобки можно оставить пустыми.
    await callback.answer('Товар удален')

    # А здесь просто придет сообщение в личку, что товар удален.
    await callback.message.answer('Товар удален')

################# Микро FSM для загрузки/изменения баннеров ############### noqa


class AddBanner(StatesGroup):
    name = State()
    image = State()


@admin_router.message(StateFilter(None), F.text == 'Добавить/Изменить баннер')
async def update_banner(
        message: types.Message,
        state: FSMContext,
        session: AsyncSession
):
    pages = {
        page.name: str(page.id)
        for page in await banner_crud.get_multi(session=session)
    }
    pages['ОТМЕНИТЬ'] = 'cancel'
    await message.answer(
        'Выберите имя баннера:',
        reply_markup=get_callback_btns(btns=pages)
    )
    await state.set_state(AddBanner.name)


@admin_router.callback_query(AddBanner.name, F.data.regexp(r'^[\d]+'))
async def get_banner_for_change(
        callback: types.CallbackQuery,
        state: FSMContext,
        session: AsyncSession
):
    banner_id = int(callback.data)
    await state.update_data(banner_id=banner_id)
    banner = await banner_crud.get(obj_id=banner_id, session=session)
    await callback.answer()
    await callback.message.answer(
        f"Отправьте фото для баннера {banner.name}."
    )
    await state.set_state(AddBanner.image)


@admin_router.message(AddBanner.image, F.photo)
async def add_banner_image(
        message: types.Message,
        state: FSMContext,
        session: AsyncSession
):
    await state.update_data(image=message.photo[-1].file_id)
    data = await state.get_data()
    await banner_crud.update(
        obj_id=data.pop('banner_id'),
        data=data,
        session=session
    )
    await message.answer("Баннер добавлен/изменен.")
    await state.clear()


# ловим некоррекный ввод
@admin_router.message(AddBanner.image)
async def fix_banner_image(message: types.Message, state: FSMContext):
    await message.answer("Отправьте фото баннера или отмена")

##############################################################


# КОД НИЖЕ ДЛЯ МАШИНЫ СОСТОЯНИЙ (FSM)


@admin_router.callback_query(StateFilter(None), F.data.startswith('change_'))
async def change_product(
        callback: types.CallbackQuery,
        state: FSMContext,
        # session: AsyncSession
):
    product_id = int(callback.data.split('_')[-1])
    # product = await product_crud.get(obj_id=product_id, session=session)
    AddProduct.change_product_id = product_id
    await callback.answer()
    await callback.message.answer(
        text='Введите название товара',
        reply_markup=FSM_MANAGEMENT_KB
    )
    # Нужно указать в какое состояние нужно стать
    await state.set_state(AddProduct.name)


# 1) FSM начнется, если у пользователя
# нет активных состояний - StateFilter(None).
# Это точка входа в состояние.
@admin_router.message(StateFilter(None), F.text == 'Добавить товар')
async def add_product_fsm(message: types.Message, state: FSMContext):
    await message.answer(
        text='Введите название товара',
        reply_markup=FSM_MANAGEMENT_KB
    )
    # Нужно указать в какое состояние нужно стать
    await state.set_state(AddProduct.name)


# Сбросить состояние пользователя.
# '*' - обозначает любое состояние пользователя.
@admin_router.callback_query(StateFilter('*'), F.data == 'cancel')
@admin_router.message(StateFilter('*'), Command('отмена'))
@admin_router.message(StateFilter('*'), F.text.casefold() == 'отмена')
async def cancel_fsm(message: types.Message, state: FSMContext) -> None:
    # Сохраним текущее состояние в переменную.
    current_state = state.get_state()
    # Если у пользователя нет никакого состояния ..
    if current_state is None:
        # Завершаем работу хендлера.
        return
    if AddProduct.change_product_id:
        AddProduct.change_product_id = None
    # В ином случае очищаем данные и убираем все состояния.
    await state.clear()
    await message.answer(
        text='Все действия отменены',
        reply_markup=ADMIN_KB
    )


@admin_router.message(StateFilter('*'), Command('назад'))
@admin_router.message(StateFilter('*'), F.text.casefold() == 'назад')
async def back_fsm(message: types.Message, state: FSMContext) -> None:
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
            await state.set_state(previous)
            await message.answer(
                'Вы вернулись к прошлому шагу '
                f'\n {AddProduct.texts[previous.state]}'
            )
            return
        previous = step


# 2) Если пользователь в состоянии AddProduct.name и ввел текст,
# то продолжаем FSM
@admin_router.message(
    AddProduct.name,
    or_f(F.text.strip().lower() == 'пропустить', F.text)
)
async def add_name_fsm(message: types.Message, state: FSMContext):
    if 'пропустить' in message.text.lower():
        pass
    else:
        # Записываем name из предыдущего шага
        await state.update_data(name=message.text)
    await message.answer(
        text='Введите описание товара'
    )
    print()
    print(f'{AddProduct.change_product_id=} {message.from_user.username}')
    print()
    # Меняем состояние на description
    await state.set_state(AddProduct.description)


# Если вместо текста будет другое событие,
# то выполнится этот хендлер, но состояние останется прежним.
@admin_router.message(AddProduct.name)
async def fix_name_fsm(message: types.Message):
    await message.reply(
        text=(
            'Название товара было введено некорректно, '
            'введите название еще раз'
        )
    )


# 3) Если пользователь в состоянии AddProduct.description и ввел текст,
# то продолжаем FSM
@admin_router.message(
    AddProduct.description,
    or_f(F.text.strip().lower() == 'пропустить', F.text)
)
async def add_description_fsm(
        message: types.Message,
        state: FSMContext,
        session: AsyncSession
):
    if 'пропустить' in message.text.lower():
        pass
    else:
        # Записываем description
        await state.update_data(description=message.text)

    categories = await category_crud.get_multi(session=session)
    categories_keyboard = get_callback_btns(btns={
        category.name: str(category.id)
        for category in categories
    })
    await message.answer(
        text='Выберите категорию товара', reply_markup=categories_keyboard
    )
    # Меняем состояние на category
    await state.set_state(AddProduct.category)


@admin_router.message(AddProduct.description)
async def fix_description_fsm(message: types.Message):
    await message.reply(
        text=(
            'Описание товара было введено некорректно, '
            'введите описание еще раз'
        )
    )


# 4) Ловим callback выбора категории
@admin_router.callback_query(AddProduct.category)
async def add_category(
        callback: types.CallbackQuery,
        state: FSMContext,
        session: AsyncSession
):
    if int(callback.data) in [
        category.id
        for category in await (
            category_crud.get_multi(session=session)
        )
    ]:
        await callback.answer()
        await state.update_data(category_id=int(callback.data))
        await callback.message.answer('Теперь введите цену товара.')
        await state.set_state(AddProduct.price)
    else:
        await callback.message.answer('Выберите катеорию из кнопок.')
        await callback.answer()


# Ловим любые некорректные действия, кроме нажатия на кнопку выбора категории
@admin_router.message(AddProduct.category)
async def category_choice2(message: types.Message, state: FSMContext):
    await message.answer("'Выберите катеорию из кнопок.'")


# 5) Если пользователь в состоянии AddProduct.price и ввел текст,
# то продолжаем FSM
@admin_router.message(
    AddProduct.price,
    or_f(F.text.strip().lower() == 'пропустить', F.text)
)
async def add_price_fsm(message: types.Message, state: FSMContext):
    if 'пропустить' in message.text.lower():
        pass
    else:
        # Записываем price
        await state.update_data(price=float(message.text))
    await message.answer(
        text='Загрузите изображение товара'
    )
    # Меняем состояние на image
    await state.set_state(AddProduct.image)


@admin_router.message(AddProduct.price)
async def fix_price_fsm(message: types.Message):
    await message.reply(
        text=(
            'Цена товара была введена некорректно, '
            'введите цену еще раз'
        )
    )


# 6) Если пользователь в состоянии AddProduct.image и загрузил фото,
# то продолжаем FSM
@admin_router.message(
    AddProduct.image,
    or_f(F.text.strip().lower() == 'пропустить', F.photo)
)
async def add_image_fsm(
        message: types.Message,
        state: FSMContext,
        session: AsyncSession
):
    if message.text and 'пропустить' in message.text.lower():
        pass
    else:
        # Записываем в словарь фото.
        # photo[-1] - означает самое высокое качество,
        # так как на серверах хранится несколько вариантов фото.
        # К каждому изображению ТГ присваивает уникальные id
        await state.update_data(image=message.photo[-1].file_id)
    await message.answer(
        text='Товар добавлен/изменен',
        reply_markup=ADMIN_KB
    )
    # Теперь полученные данные можно куда-нибудь сохранить.
    data = await state.get_data()
    print()
    print(data)
    print()
    if AddProduct.change_product_id:
        await product_crud.update(
            obj_id=int(AddProduct.change_product_id),
            data=data, session=session
        )
        AddProduct.change_product_id = None
    else:
        await product_crud.create(obj_in=data, session=session)
    # Когда пользователь прошел все пункты -
    # очистить состояние пользователя и удалить все данные из машины состояния!
    await state.clear()


@admin_router.message(AddProduct.image)
async def fix_image_fsm(message: types.Message):
    await message.reply(
        text=(
            'Некорректный тип изображения, '
            'попробуйте загрузить другое'
        )
    )
