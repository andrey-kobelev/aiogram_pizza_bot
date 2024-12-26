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
    await callback.answer('Товар удален')
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


@admin_router.message(AddBanner.image)
async def fix_banner_image(message: types.Message, state: FSMContext):
    await message.answer("Отправьте фото баннера или отмена")

##############################################################


# КОД НИЖЕ ДЛЯ МАШИНЫ СОСТОЯНИЙ (FSM)


@admin_router.callback_query(StateFilter(None), F.data.startswith('change_'))
async def change_product(
        callback: types.CallbackQuery,
        state: FSMContext,
):
    product_id = int(callback.data.split('_')[-1])
    AddProduct.change_product_id = product_id
    await callback.answer()
    await callback.message.answer(
        text='Введите название товара',
        reply_markup=FSM_MANAGEMENT_KB
    )
    await state.set_state(AddProduct.name)


@admin_router.message(StateFilter(None), F.text == 'Добавить товар')
async def add_product_fsm(message: types.Message, state: FSMContext):
    await message.answer(
        text='Введите название товара',
        reply_markup=FSM_MANAGEMENT_KB
    )
    await state.set_state(AddProduct.name)


@admin_router.callback_query(StateFilter('*'), F.data == 'cancel')
@admin_router.message(StateFilter('*'), Command('отмена'))
@admin_router.message(StateFilter('*'), F.text.casefold() == 'отмена')
async def cancel_fsm(message: types.Message, state: FSMContext) -> None:
    current_state = state.get_state()
    if current_state is None:
        return
    if AddProduct.change_product_id:
        AddProduct.change_product_id = None
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


@admin_router.message(
    AddProduct.name,
    or_f(F.text.strip().lower() == 'пропустить', F.text)
)
async def add_name_fsm(message: types.Message, state: FSMContext):
    if 'пропустить' in message.text.lower():
        pass
    else:
        await state.update_data(name=message.text)
    await message.answer(
        text='Введите описание товара'
    )
    await state.set_state(AddProduct.description)


@admin_router.message(AddProduct.name)
async def fix_name_fsm(message: types.Message):
    await message.reply(
        text=(
            'Название товара было введено некорректно, '
            'введите название еще раз'
        )
    )


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
        await state.update_data(description=message.text)

    categories = await category_crud.get_multi(session=session)
    categories_keyboard = get_callback_btns(btns={
        category.name: str(category.id)
        for category in categories
    })
    await message.answer(
        text='Выберите категорию товара', reply_markup=categories_keyboard
    )
    await state.set_state(AddProduct.category)


@admin_router.message(AddProduct.description)
async def fix_description_fsm(message: types.Message):
    await message.reply(
        text=(
            'Описание товара было введено некорректно, '
            'введите описание еще раз'
        )
    )


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


@admin_router.message(AddProduct.category)
async def category_choice2(message: types.Message, state: FSMContext):
    await message.answer("'Выберите катеорию из кнопок.'")


@admin_router.message(
    AddProduct.price,
    or_f(F.text.strip().lower() == 'пропустить', F.text)
)
async def add_price_fsm(message: types.Message, state: FSMContext):
    if 'пропустить' in message.text.lower():
        pass
    else:
        await state.update_data(price=float(message.text))
    await message.answer(
        text='Загрузите изображение товара'
    )
    await state.set_state(AddProduct.image)


@admin_router.message(AddProduct.price)
async def fix_price_fsm(message: types.Message):
    await message.reply(
        text=(
            'Цена товара была введена некорректно, '
            'введите цену еще раз'
        )
    )


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
        await state.update_data(image=message.photo[-1].file_id)
    await message.answer(
        text='Товар добавлен/изменен',
        reply_markup=ADMIN_KB
    )
    data = await state.get_data()
    if AddProduct.change_product_id:
        await product_crud.update(
            obj_id=int(AddProduct.change_product_id),
            data=data, session=session
        )
        AddProduct.change_product_id = None
    else:
        await product_crud.create(obj_in=data, session=session)
    await state.clear()


@admin_router.message(AddProduct.image)
async def fix_image_fsm(message: types.Message):
    await message.reply(
        text=(
            'Некорректный тип изображения, '
            'попробуйте загрузить другое'
        )
    )
