import os

import dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base
from app.crud import category_crud, banner_crud
from app.common.texts_for_db import categories, description_for_info_pages

dotenv.load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL_AS_BOT')


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


async def import_data():
    async with AsyncSessionLocal() as session:
        await category_crud.create_categories(session=session, categories=categories)
        await banner_crud.create_multiple(session=session, obj_in=description_for_info_pages)