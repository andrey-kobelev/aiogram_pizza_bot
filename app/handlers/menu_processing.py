from aiogram.types import InputMediaPhoto
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import banner_crud, category_crud, product_crud, cart_crud
from app.keyboards.inline import (
    get_products_keyboard,
    get_main_keyboard,
    get_catalog_keyboard,
    get_user_cart_keyboard,
    MenuCallBack
)
from app.utils.paginator import Paginator


async def main_menu(session: AsyncSession, data: MenuCallBack):
    banner = await banner_crud.get_by_name(
        obj_name=data.menu_name, session=session
    )
    image = InputMediaPhoto(media=banner.image, caption=banner.description)
    keyboard = get_main_keyboard()
    return image, keyboard


async def catalog(session: AsyncSession, data: MenuCallBack):
    banner = await banner_crud.get_by_name(
        obj_name=data.menu_name, session=session
    )
    image = InputMediaPhoto(media=banner.image, caption=banner.description)
    categories = await category_crud.get_multi(session=session)
    keyboard = get_catalog_keyboard(categories=categories)
    return image, keyboard


async def products(session: AsyncSession, data: MenuCallBack):
    products = await product_crud.get_multi(
        session=session,
        category_id=data.category_id
    )

    paginator = Paginator(products, page=data.page)
    product = paginator.get_page()[0]

    image = InputMediaPhoto(
        media=product.image,
        caption=(
            f"<strong>{product.name}</strong>\n"
            f"{product.description}\n"
            f"Стоимость: {round(product.price, 2)}\n"
            f"<strong>Товар {paginator.page} из {paginator.pages}</strong>"
        ),
    )

    keyboard = get_products_keyboard(
        level=data.level,
        category_id=data.category_id,
        page=data.page,
        product_id=product.id,
        paginator=paginator
    )

    return image, keyboard


async def carts(
        session: AsyncSession, data: MenuCallBack
):
    if data.menu_name == "delete":
        await cart_crud.delete_from_cart(
            session=session,
            user_id=data.user_id,
            product_id=data.product_id
        )
        if data.page > 1:
            data.page -= 1
    elif data.menu_name == "decrement":
        is_cart = await cart_crud.decrement_cart_product(
            session=session,
            user_id=data.user_id,
            product_id=data.product_id
        )
        if data.page > 1 and not is_cart:
            data.page -= 1
    elif data.menu_name == "increment":
        await cart_crud.add_to_cart(
            session=session,
            user_id=data.user_id,
            product_id=data.product_id
        )

    carts = await cart_crud.get_user_carts(
        session=session, user_id=data.user_id
    )

    if not carts:
        banner = await banner_crud.get_by_name(
            session=session,
            obj_name="cart"
        )
        image = InputMediaPhoto(
            media=banner.image,
            caption=f"<strong>{banner.description}</strong>"
        )

        kbds = get_user_cart_keyboard(
            level=data.level,
            page=None,
            product_id=None,
        )
    else:
        paginator = Paginator(carts, page=data.page)

        cart = paginator.get_page()[0]

        cart_price = round(cart.quantity * cart.product.price, 2)
        total_price = round(
            sum(cart.quantity * cart.product.price for cart in carts), 2
        )
        image = InputMediaPhoto(
            media=cart.product.image,
            caption=(
                f"<strong>{cart.product.name}</strong>\n"
                f"{round(cart.product.price, 2)}$ "
                f"x {cart.quantity} = {cart_price}$\n"
                f"Товар {paginator.page} из {paginator.pages} в корзине.\n"
                f"Общая стоимость товаров в корзине {total_price}"
            ),
        )

        kbds = get_user_cart_keyboard(
            level=data.level,
            page=data.page,
            product_id=cart.product.id,
            paginator=paginator
        )

    return image, kbds


async def get_menu_content(
        session: AsyncSession,
        data: MenuCallBack
):
    levels = {
        0: main_menu,
        1: catalog,
        2: products,
        3: carts
    }
    return await levels[data.level](session=session, data=data)
