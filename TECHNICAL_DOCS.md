# Техническая документация проекта "Бот-пиццерия"

## Оглавление
1. [Обзор системы](#обзор-системы)
2. [Архитектура приложения](#архитектура-приложения)
3. [Структура проекта](#структура-проекта)
4. [Модели данных](#модели-данных)
5. [Обработчики и роутеры](#обработчики-и-роутеры)
6. [Middleware и фильтры](#middleware-и-фильтры)
7. [Конфигурация](#конфигурация)
8. [База данных](#база-данных)
9. [Руководство разработчика](#руководство-разработчика)
10. [API Reference](#api-reference)

## Обзор системы

Telegram бот-пиццерия представляет собой полнофункциональное приложение для онлайн заказа пиццы через Telegram. Система включает в себя:

- **Клиентская часть**: Интерфейс для пользователей с каталогом товаров, корзиной и оформлением заказов
- **Административная панель**: Управление товарами, категориями и баннерами
- **Система авторизации**: Автоматическое создание пользователей и управление правами доступа
- **База данных**: SQLite с ORM SQLAlchemy для хранения данных

### Ключевые функции
- Многоуровневое меню навигации
- Каталог товаров с категориями
- Корзина покупок
- Постраничная навигация (пагинация)
- Административная панель для управления контентом
- Система баннеров и статической информации

## Архитектура приложения

Приложение построено по модульной архитектуре с разделением ответственности:

```
Bot Application
├── Presentation Layer (handlers)
├── Business Logic Layer (crud)
├── Data Access Layer (models)
├── Infrastructure Layer (core, middlewares)
└── Static Resources (static)
```

### Технологический стек

- **Python 3.9+** - Основной язык программирования
- **Aiogram 3.13** - Асинхронный фреймворк для Telegram Bot API
- **SQLAlchemy 2.0** - ORM для работы с базой данных
- **Alembic 1.13** - Система миграций базы данных
- **aiosqlite 0.20** - Асинхронный драйвер для SQLite
- **Pydantic 2.9** - Валидация данных

## Структура проекта

```
app/
├── main.py                 # Точка входа в приложение
├── __init__.py
├── common/                 # Общие компоненты
│   └── texts_for_db.py    # Тексты для инициализации БД
├── core/                   # Ядро приложения
│   ├── base.py            # Базовые настройки
│   └── db.py              # Конфигурация базы данных
├── crud/                   # CRUD операции
│   ├── banner.py          # Операции с баннерами
│   ├── cart.py            # Операции с корзиной
│   ├── category.py        # Операции с категориями
│   ├── product.py         # Операции с товарами
│   └── user.py            # Операции с пользователями
├── filters/                # Фильтры для обработчиков
│   └── chat_types.py      # Фильтры типов чатов
├── handlers/               # Обработчики команд и сообщений
│   ├── admin_private.py   # Административные команды
│   ├── menu_processing.py # Обработка меню
│   ├── user_group.py      # Групповые команды
│   └── user_private.py    # Пользовательские команды
├── keyboards/              # Клавиатуры и кнопки
│   ├── inline.py          # Inline клавиатуры
│   └── reply.py           # Reply клавиатуры
├── middlewares/            # Промежуточное ПО
│   └── db.py              # Middleware для БД и пользователей
├── models/                 # Модели данных
│   ├── abstract_models.py # Абстрактные базовые модели
│   ├── banner.py          # Модель баннеров
│   ├── base.py            # Базовая модель
│   ├── cart.py            # Модель корзины
│   ├── category.py        # Модель категорий
│   ├── product.py         # Модель товаров
│   └── user.py            # Модель пользователей
├── static/                 # Статические файлы
└── utils/                  # Утилиты
    └── paginator.py       # Пагинация
```

## Модели данных

### Диаграмма связей
```
User (1) ----< Cart (N)
Category (1) ----< Product (N)
Product (1) ----< Cart (N)
Banner (standalone)
```

### User (Пользователь)
```python
class User(BaseDateTimeFields):
    user_id: int           # Telegram ID пользователя (уникальный)
    first_name: str        # Имя (до 150 символов)
    last_name: str         # Фамилия (до 150 символов)  
    phone: str             # Телефон (до 13 символов)
    created_at: datetime   # Дата создания
    updated_at: datetime   # Дата обновления
```

### Category (Категория)
```python
class Category(BaseDateTimeFields, BaseNameField):
    name: str              # Название категории (уникальное)
    created_at: datetime   # Дата создания
    updated_at: datetime   # Дата обновления
    products: List[Product] # Связанные товары
```

### Product (Товар)
```python
class Product(BaseDateTimeFields, BaseNameField, BaseImageDescriptionFields):
    name: str              # Название товара
    description: str       # Описание
    image: str            # Путь к изображению
    price: float          # Цена (с поддержкой десятичных)
    category_id: int      # ID категории (FK)
    category: Category    # Связанная категория
    created_at: datetime  # Дата создания
    updated_at: datetime  # Дата обновления
```

### Cart (Корзина)
```python
class Cart(BaseDateTimeFields):
    user_id: int          # ID пользователя (FK)
    product_id: int       # ID товара (FK)
    quantity: int         # Количество
    user: User           # Связанный пользователь
    product: Product     # Связанный товар
    created_at: datetime # Дата создания
    updated_at: datetime # Дата обновления
```

### Banner (Баннер)
```python
class Banner(BaseDateTimeFields, BaseNameField, BaseImageDescriptionFields):
    name: str             # Название баннера
    description: str      # Текст баннера
    image: str           # Путь к изображению
    created_at: datetime # Дата создания
    updated_at: datetime # Дата обновления
```

## Обработчики и роутеры

### Пользовательские обработчики (`user_private.py`)
- `/start` - Приветствие и главное меню
- `/menu` - Каталог товаров
- `/cart` - Просмотр корзины
- `/about` - Информация о пиццерии
- `/payment` - Информация об оплате
- `/shipping` - Информация о доставке

### Административные обработчики (`admin_private.py`)
- `/admin` - Панель администратора
- Управление товарами (добавление, редактирование, удаление)
- Управление категориями
- Управление баннерами
- Загрузка изображений

### Обработчики меню (`menu_processing.py`)
- Навигация по категориям
- Просмотр товаров с пагинацией
- Добавление в корзину
- Изменение количества товаров

### Групповые обработчики (`user_group.py`)
- `/admin` - Добавление администратора (только в группах)

## Middleware и фильтры

### DBSession Middleware
Обеспечивает доступ к сессии базы данных во всех обработчиках:
```python
async def __call__(self, handler, event, data):
    async with self.async_session() as session:
        data['session'] = session
        return await handler(event, data)
```

### CreateUserMiddleware
Автоматически создает пользователя при первом взаимодействии:
```python
async def __call__(self, handler, event, data):
    user = event.from_user
    if user:
        # Создание или обновление пользователя в БД
```

### Фильтры типов чатов
- `ChatTypeFilter` - Фильтрация по типу чата (приватный/группа)
- `IsAdmin` - Проверка административных прав

## Конфигурация

### Переменные окружения (.env)
```env
BOT_TOKEN=your_bot_token_here
DATABASE_URL=sqlite+aiosqlite:///absolute/path/to/pizza_store_bot.db
```

### Настройки базы данных
```python
# app/core/db.py
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)
```

## База данных

### Миграции (Alembic)
Система использует Alembic для управления схемой базы данных:

```bash
# Создание новой миграции
alembic revision --autogenerate -m "description"

# Применение миграций
alembic upgrade head

# Откат миграций
alembic downgrade -1
```

### Инициализация данных
При запуске автоматически создаются:
- Базовые категории товаров
- Информационные баннеры

## Руководство разработчика

### Добавление нового обработчика
1. Создайте функцию-обработчик в соответствующем файле
2. Зарегистрируйте роутер в `handlers/__init__.py`
3. Добавьте необходимые клавиатуры в `keyboards/`

### Создание новой модели
1. Определите модель в `models/`
2. Создайте CRUD операции в `crud/`
3. Сгенерируйте и примените миграцию

### Добавление middleware
1. Создайте класс middleware в `middlewares/`
2. Зарегистрируйте в `main.py`

### Стиль кода
- Используйте async/await для всех операций с БД
- Следуйте PEP 8
- Добавляйте type hints
- Используйте meaningful имена переменных

### Тестирование
```bash
# Запуск проверки кода
flake8 app/

# Запуск с отладкой
python -m app.main
```

## API Reference

### CRUD операции

#### UserCRUD
```python
async def create_user(session: AsyncSession, user_data: dict) -> User
async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> User
async def update_user(session: AsyncSession, user: User, update_data: dict) -> User
```

#### ProductCRUD
```python
async def get_products_by_category(session: AsyncSession, category_id: int) -> List[Product]
async def create_product(session: AsyncSession, product_data: dict) -> Product
async def update_product(session: AsyncSession, product_id: int, update_data: dict) -> Product
async def delete_product(session: AsyncSession, product_id: int) -> None
```

#### CartCRUD
```python
async def add_to_cart(session: AsyncSession, user_id: int, product_id: int, quantity: int) -> Cart
async def get_user_cart(session: AsyncSession, user_id: int) -> List[Cart]
async def update_cart_item(session: AsyncSession, cart_id: int, quantity: int) -> Cart
async def clear_cart(session: AsyncSession, user_id: int) -> None
```

### Утилиты

#### Paginator
```python
class Paginator:
    def __init__(self, array: list, page: int = 0, per_page: int = 1)
    def get_page(self) -> list
    def has_previous(self) -> bool  
    def has_next(self) -> bool
    def get_previous_page(self) -> int
    def get_next_page(self) -> int
```

## Безопасность

### Права доступа
- Административные функции доступны только пользователям в списке `bot.admins`
- Проверка прав происходит через фильтры
- Пользователи добавляются в админы через команду `/admin` в группе

### Валидация данных
- Использование Pydantic для валидации входных данных
- Проверка типов файлов при загрузке изображений
- Санитизация пользовательского ввода

## Масштабирование

### Рекомендации по оптимизации
1. **База данных**: Переход на PostgreSQL для больших нагрузок
2. **Кэширование**: Использование Redis для кэширования частых запросов
3. **Файлы**: Использование CDN для статических файлов
4. **Мониторинг**: Добавление логирования и метрик

### Возможные улучшения
- Система оплаты (интеграция с платежными системами)
- Уведомления администраторов о новых заказах
- Система скидок и промокодов
- Мультиязычность
- Геолокация для расчета доставки