from sqlalchemy import Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .abstract_models import (
    BaseDateTimeFields,
    BaseNameField,
    BaseImageDescriptionFields
)


NAME_LENGTH = 150


class Product(BaseDateTimeFields, BaseNameField, BaseImageDescriptionFields):
    price: Mapped[float] = mapped_column(Float(asdecimal=True), nullable=False)
    category_id: Mapped[int] = mapped_column(
        ForeignKey(
            column='category.id',
            name='fk_product_category_id_category',
            ondelete='CASCADE'
        ),
        nullable=False
    )

    category: Mapped['Category'] = relationship(backref='products') # noqa
