from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .abstract_models import BaseDateTimeFields


class Cart(BaseDateTimeFields):
    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            column='user.user_id',
            ondelete='CASCADE',
            name='fk_cart_user_id_user'
        ),
        nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey(
            column='product.id',
            ondelete='CASCADE',
            name='fk_cart_product_id_product'
        ),
        nullable=False
    )
    quantity: Mapped[int]

    user: Mapped['User'] = relationship(backref='cart') # noqa
    product: Mapped['Product'] = relationship(backref='cart') # noqa
