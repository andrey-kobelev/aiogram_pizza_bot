import os

import dotenv
from sqlalchemy import Column, Integer
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declared_attr, sessionmaker, DeclarativeBase

dotenv.load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL_AS_BOT')


class Base(DeclarativeBase):

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)


engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_async_session():
    async with AsyncSessionLocal() as async_session:
        yield async_session


# Что-бы вручную создать БД
async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
