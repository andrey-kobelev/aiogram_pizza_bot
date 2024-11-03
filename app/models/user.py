from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from .abstract_models import BaseDateTimeFields


PHONE_LENGTH = 13
LAST_NAME_LENGTH = 150
FIRST_NAME_LENGTH = 150


class User(BaseDateTimeFields):
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    first_name: Mapped[str] = mapped_column(
        String(FIRST_NAME_LENGTH), nullable=True
    )
    last_name: Mapped[str] = mapped_column(
        String(LAST_NAME_LENGTH), nullable=True
    )
    phone: Mapped[str] = mapped_column(String(PHONE_LENGTH), nullable=True)
