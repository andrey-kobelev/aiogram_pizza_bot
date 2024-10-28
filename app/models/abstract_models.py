from sqlalchemy import (
    DateTime,
    func
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class BaseFields(Base):
    __abstract__ = True

    create_date: Mapped[DateTime] = mapped_column(
        DateTime, index=True, default=func.now()
    )
    update_date: Mapped[DateTime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )
