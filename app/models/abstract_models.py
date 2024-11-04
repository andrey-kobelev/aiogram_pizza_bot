from sqlalchemy import (
    DateTime,
    func,
    String, Text
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


NAME_LENGTH = 150
IMAGE_LENGTH = 150


class BaseDateTimeFields(Base):
    __abstract__ = True

    create_date: Mapped[DateTime] = mapped_column(
        DateTime, index=True, default=func.now()
    )
    update_date: Mapped[DateTime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )


class BaseNameField(Base):
    __abstract__ = True

    name: Mapped[str] = mapped_column(
        String(NAME_LENGTH), unique=True, nullable=False
    )


class BaseImageDescriptionFields(Base):
    __abstract__ = True

    image: Mapped[str] = mapped_column(String(IMAGE_LENGTH), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
