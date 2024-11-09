from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from .base import CRUDBase
from app.models import Cart


class CRUDCart(CRUDBase):

    async def add_to_cart(
            self,
            session: AsyncSession,
            user_id: int,
            product_id: int
    ):
        query = select(Cart).where(
            self.model.user_id == user_id,
            self.model.product_id == product_id
        )
        cart = await session.execute(query)
        cart = cart.scalar()
        if cart:
            cart.quantity += 1
            await session.commit()
            return cart
        else:
            session.add(Cart(
                user_id=user_id,
                product_id=product_id,
                quantity=1
            ))
            await session.commit()

    async def get_user_carts(
            self,
            session: AsyncSession,
            user_id
    ):
        query = select(self.model).filter(
            self.model.user_id == user_id
        ).options(joinedload(Cart.product))
        result = await session.execute(query)
        return result.scalars().all()

    async def delete_from_cart(
            self,
            session: AsyncSession,
            user_id: int,
            product_id: int
    ):
        query = delete(self.model).where(
            self.model.user_id == user_id,
            self.model.product_id == product_id
        )
        await session.execute(query)
        await session.commit()

    async def decrement_cart_product(
            self,
            session: AsyncSession,
            user_id: int,
            product_id: int
    ):
        query = select(self.model).where(
            self.model.user_id == user_id,
            self.model.product_id == product_id
        ).options(
            joinedload(self.model.product))
        cart = await session.execute(query)
        cart = cart.scalar()

        if not cart:
            return
        if cart.quantity > 1:
            cart.quantity -= 1
            await session.commit()
            return True
        else:
            await self.delete_from_cart(session, user_id, product_id)
            await session.commit()
            return False


cart_crud = CRUDCart(model=Cart)
