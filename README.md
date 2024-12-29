# Бот-пиццерия

> Бот-пиццерия - здесь вы сможете выбрать пиццу и напитки, добавить их в корзину и оформить заказ.

Написал бота на Aiogram3 с многоуровневым меню. Написал админку для управления товарами и баннерами для отображения меню. Подключил базу данных SQLite на асинхронном движке и ORM SQLAlchemy. Реализовал возможность для пользователей выбрать товары из определенной категории и добавлять их в корзину для последующего заказа. Добавил пагинатор для постраничного отображения товаров. Для каждого хендлера прописал права доступа (одни для админа, другие для обычного пользователя). В коде есть моменты которые трубуют рефакторинг, например админка.

#### Статус
Дальше бот развивать не планирую.

### Развернуть проект локально

Клонировать репозиторий и перейти в него в командной строке:  
  
```  
git clone https://github.com/andrey-kobelev/aiogram_pizza_bot.git
```  
  
```  
cd aiogram_pizza_bot
```  
  
Cоздать и активировать виртуальное окружение:  
  
```  
python3 -m venv venv  
```  
  
```  
source venv/bin/activate  
```  
  
Установить зависимости из файла requirements.txt:  
  
```  
python3 -m pip install --upgrade pip  
```  
  
```  
pip install -r requirements.txt  
```

## Файл .env

Файл .env должен содержать переменную BOT_TOKEN - разместите этот файл в корне проекта. Создайте бота и получите токен через BotFather в telegram, полученный токен присвойте переменной BOT_TOKEN.

Для работы БД так же должна быть переменная DATABASE_URL. Важно, путь к файлу БД должен быть абсолютным, вот пример: `DATABASE_URL=sqlite+aiosqlite:///<full_path_to_db_file>/pizza_store_bot.db`

## Запустить бот
Перед тем как начать: 
1. Создайте ТГ группу, 
2. добавьте в группу бота и назначьте бота администратором группы, дав ему все права для управления группой.
3. После того как добавите бота в группу, сделайте запрет для добавления бота в другие группы или каналы (это делается через BotFather)
4. Находясь в корневой директории проекта выполните команду в терминале

```
python -m app.main
```

5. Находясь в группе введите команду в окно для ввода сообщения: `/admin`. Таким образом бот добавит вас в свой список администраторов и вы сможете пользоваться админкой.
6. Зайдите в бота и введите команду `/admin`. Вы увидите кнопки админки. Вам нужна кнопка `Добавить/Изменить баннер` - нажмите на нее. Далее вы увидите список всех баннеров - вам нужно для каждого баннера задать картинку (это обязательно! иначе бот не будет работать должным образом). Картинки хранятся в директории `static` в корне проекта, и имена картинок соответствуют именам баннеров. PS: Если ошибетесь на этом моменте, то нажмите `/start` а затем обратно `/admin` - это поможет как бы перезагрузиться. ВНИМАНИЕ: картинки нужно загружать через самого бота.

7. Готово! Нажимайте `/start` и пользуйтесь ботом!

> [!WARNING]\
>  При оформлении заказа ничего не произойдет, эту фичу нужно допиливать по ситуации, готовить пиццы то некому!))


### Автор 
- Кобелев Андрей
    - [email](mailto:andrew.a.kobelev@yandex.ru)


> Проект писался на основе курса на PythonHub Studio

### Стек технологий

- ##### [Python 3.9](https://www.python.org/downloads/release/python-390/)
- ##### [Alembic](https://alembic.sqlalchemy.org/en/latest/index.html)
- ##### [SQLAlchemy](https://docs.sqlalchemy.org/en/20/)
- ##### [Aiogram3](https://docs.aiogram.dev/en/v3.15.0/)
- ##### [Alembic](https://www.python.org/downloads/release/python-390/)
- ##### [aiosqlite](https://aiosqlite.omnilib.dev/en/stable/index.html)

