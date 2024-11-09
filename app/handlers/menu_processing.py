from typing import Optional

from aiogram.types import InputMediaPhoto
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import banner_crud, category_crud, product_crud, cart_crud
from app.keyboards.inline import (
    get_products_keyboard,
    get_main_keyboard,
    get_catalog_keyboard,
    get_user_cart
)
from app.utils.paginator import Paginator


async def main_menu(session: AsyncSession, level: int, menu_name: str):
    print()
    print(f'{menu_name=}')
    print()
    banner = await banner_crud.get_by_name(obj_name=menu_name, session=session)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)
    keyboard = get_main_keyboard(level=level)
    return image, keyboard


async def catalog(session: AsyncSession, level: int, menu_name: str):
    banner = await banner_crud.get_by_name(obj_name=menu_name, session=session)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)
    categories = await category_crud.get_multi(session=session)
    keyboard = get_catalog_keyboard(level=level, categories=categories)
    return image, keyboard


def get_next_previous_buttons(paginator: Paginator):
    buttons = dict()
    if paginator.has_previous():
        buttons["◀ Пред."] = "previous"

    if paginator.has_next():
        buttons["След. ▶"] = "next"

    return buttons


async def products(
        session: AsyncSession,
        level: int,
        category_id: int,
        page: int
):
    products = await product_crud.get_multi(
        session=session,
        category_id=category_id
    )

    paginator = Paginator(products, page=page)
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

    next_previous_buttons = get_next_previous_buttons(paginator)

    kbds = get_products_keyboard(
        level=level,
        category_id=category_id,
        page=page,
        next_previous_buttons=next_previous_buttons,
        product_id=product.id,
    )

    return image, kbds


async def carts(
        session: AsyncSession,
        level: int,
        menu_name: str,
        page: int,
        user_id: int,
        product_id: int
):
    if menu_name == "delete":
        await cart_crud.delete_from_cart(
            session=session,
            user_id=user_id,
            product_id=product_id
        )
        if page > 1:
            page -= 1
    elif menu_name == "decrement":
        is_cart = await cart_crud.decrement_cart_product(
            session=session,
            user_id=user_id,
            product_id=product_id
        )
        if page > 1 and not is_cart:
            page -= 1
    elif menu_name == "increment":
        await cart_crud.add_to_cart(
            session=session,
            user_id=user_id,
            product_id=product_id
        )

    carts = await cart_crud.get_user_carts(session=session, user_id=user_id)

    if not carts:
        banner = await banner_crud.get_by_name(
            session=session,
            obj_name="cart"
        )
        image = InputMediaPhoto(
            media=banner.image,
            caption=f"<strong>{banner.description}</strong>"
        )

        kbds = get_user_cart(
            level=level,
            page=None,
            pagination_btns=None,
            product_id=None,
        )

    else:
        paginator = Paginator(carts, page=page)

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

        pagination_btns = get_next_previous_buttons(paginator)

        kbds = get_user_cart(
            level=level,
            page=page,
            pagination_btns=pagination_btns,
            product_id=cart.product.id,
        )

    return image, kbds


async def get_menu_content(
        session: AsyncSession,
        level: int,
        menu_name: str,
        category_id: Optional[int] = None,
        page: Optional[int] = None,
        user_id: Optional[int] = None,
        product_id: Optional[int] = None,
):
    # levels = {
    #     0: await main_menu(session, level, menu_name),
    #     1: await catalog(session, level, menu_name),
    #     2: await products(
    #         session=session,
    #         level=level,
    #         category_id=category_id,
    #         page=page
    #     ),
    #     3: await carts(
    #         session=session,
    #         level=level,
    #         menu_name=menu_name,
    #         page=page,
    #         user_id=user_id,
    #         product_id=product_id
    #     )
    # }
    # return levels[level]
    if level == 0:
        return await main_menu(
            session=session,
            level=level,
            menu_name=menu_name
        )
    elif level == 1:
        return await catalog(
            session=session,
            level=level,
            menu_name=menu_name
        )
    elif level == 2:
        return await products(
            session=session,
            level=level,
            category_id=category_id,
            page=page
        )
    elif level == 3:
        return await carts(
            session=session,
            level=level,
            menu_name=menu_name,
            page=page,
            user_id=user_id,
            product_id=product_id
        )
