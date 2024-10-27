from sqlalchemy import String, Text, Float
from sqlalchemy.orm import Mapped, mapped_column

from .abstract_models import BaseFields


NAME_LENGTH = 150


class Product(BaseFields):
    name: Mapped[str] = mapped_column(
        String(NAME_LENGTH), unique=True, nullable=False
    )
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Float(asdecimal=True), nullable=False)
    image: Mapped[str] = mapped_column(String(NAME_LENGTH))
