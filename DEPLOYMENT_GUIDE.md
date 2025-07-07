# Руководство по развертыванию - Бот-пиццерия

## Содержание
1. [Требования к системе](#требования-к-системе)
2. [Подготовка окружения](#подготовка-окружения)
3. [Настройка Telegram бота](#настройка-telegram-бота)
4. [Установка и настройка приложения](#установка-и-настройка-приложения)
5. [Конфигурация базы данных](#конфигурация-базы-данных)
6. [Первый запуск и настройка](#первый-запуск-и-настройка)
7. [Настройка для production](#настройка-для-production)
8. [Мониторинг и логирование](#мониторинг-и-логирование)
9. [Резервное копирование](#резервное-копирование)
10. [Решение проблем](#решение-проблем)

## Требования к системе

### Минимальные требования
- **ОС**: Linux (Ubuntu 20.04+, CentOS 8+), macOS 10.15+, Windows 10+
- **Python**: 3.9 или выше
- **RAM**: 512 MB (минимум), 1 GB (рекомендуется)
- **Дисковое пространство**: 1 GB
- **Сеть**: Стабильное интернет-соединение

### Рекомендуемое окружение для production
- **ОС**: Ubuntu 22.04 LTS
- **Python**: 3.11
- **RAM**: 2 GB+
- **CPU**: 2 ядра
- **Дисковое пространство**: 10 GB (с учетом логов и backup)
- **База данных**: PostgreSQL (для больших нагрузок)

## Подготовка окружения

### Установка зависимостей системы

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip git sqlite3
```

#### CentOS/RHEL
```bash
sudo dnf install python3 python3-venv python3-pip git sqlite
```

#### macOS
```bash
# Установите Homebrew, если не установлен
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

brew install python@3.11 git sqlite
```

### Создание пользователя для бота (Linux)
```bash
sudo useradd -m -s /bin/bash pizzabot
sudo su - pizzabot
```

## Настройка Telegram бота

### Создание бота
1. Найдите [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте команду `/newbot`
3. Выберите имя для бота (например, "Pizza Bot")
4. Выберите username (например, "your_pizza_bot")
5. Получите токен бота (формат: `1234567890:AABCdEfGhIjKlMnOpQrStUvWxYz`)

### Настройка группы администраторов
1. Создайте группу в Telegram для администраторов
2. Добавьте бота в группу
3. Сделайте бота администратором группы со всеми правами
4. Запретите боту добавление в другие группы/каналы через @BotFather:
   - Отправьте `/mybots` в @BotFather
   - Выберите вашего бота
   - Bot Settings → Group Privacy → Turn OFF

## Установка и настройка приложения

### Клонирование репозитория
```bash
git clone https://github.com/andrey-kobelev/aiogram_pizza_bot.git
cd aiogram_pizza_bot
```

### Создание виртуального окружения
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate     # Windows
```

### Установка зависимостей
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Создание файла конфигурации
```bash
cp .env.example .env  # если есть шаблон
# или создайте новый файл:
nano .env
```

Содержимое файла `.env`:
```env
# Токен бота из BotFather
BOT_TOKEN=1234567890:AABCdEfGhIjKlMnOpQrStUvWxYz

# URL базы данных (SQLite)
DATABASE_URL=sqlite+aiosqlite:///absolute/path/to/pizza_store_bot.db

# Дополнительные настройки (опционально)
DEBUG=False
LOG_LEVEL=INFO
MAX_CART_ITEMS=50
```

**Важно**: Укажите абсолютный путь к файлу базы данных!

### Создание директорий
```bash
mkdir -p logs
mkdir -p static
mkdir -p backups
```

## Конфигурация базы данных

### SQLite (по умолчанию)
```bash
# Создание базы данных
python -c "
import asyncio
from app.core.db import create_db
asyncio.run(create_db())
"
```

### Применение миграций
```bash
# Применение всех миграций
alembic upgrade head

# Проверка статуса миграций
alembic current
alembic history
```

### PostgreSQL (для production)

#### Установка PostgreSQL
```bash
# Ubuntu
sudo apt install postgresql postgresql-contrib

# Создание пользователя и базы данных
sudo -u postgres psql
CREATE DATABASE pizza_bot;
CREATE USER pizza_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE pizza_bot TO pizza_user;
\q
```

#### Обновление конфигурации
```env
DATABASE_URL=postgresql+asyncpg://pizza_user:secure_password@localhost/pizza_bot
```

#### Установка драйвера
```bash
pip install asyncpg
```

## Первый запуск и настройка

### Тестовый запуск
```bash
python -m app.main
```

Если все настроено правильно, вы увидите:
```
Datas are importing..
Datas were imported.
Запустили бот
```

### Настройка администратора
1. В группе администраторов отправьте команду `/admin`
2. Вернитесь в личные сообщения с ботом
3. Отправьте `/admin` - вы должны увидеть административную панель
4. Настройте баннеры через "Добавить/Изменить баннер"
5. Загрузите изображения для каждого баннера

### Добавление товаров
1. Используйте административную панель для добавления категорий
2. Добавьте товары в каждую категорию
3. Загрузите изображения товаров

## Настройка для production

### Создание systemd сервиса (Linux)
```bash
sudo nano /etc/systemd/system/pizzabot.service
```

Содержимое файла:
```ini
[Unit]
Description=Pizza Bot Service
After=network.target

[Service]
Type=simple
User=pizzabot
Group=pizzabot
WorkingDirectory=/home/pizzabot/aiogram_pizza_bot
Environment=PATH=/home/pizzabot/aiogram_pizza_bot/venv/bin
ExecStart=/home/pizzabot/aiogram_pizza_bot/venv/bin/python -m app.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Активация сервиса:
```bash
sudo systemctl daemon-reload
sudo systemctl enable pizzabot.service
sudo systemctl start pizzabot.service
sudo systemctl status pizzabot.service
```

### Настройка логирования
Создайте файл `app/core/logging.py`:
```python
import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging():
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    
    # Создание форматтера
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Настройка файлового логгера
    file_handler = RotatingFileHandler(
        'logs/pizza_bot.log',
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    
    # Настройка консольного логгера
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Основной логгер
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level))
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
```

### Настройка Nginx (опционально)
Если планируете добавить веб-интерфейс:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location /static/ {
        alias /home/pizzabot/aiogram_pizza_bot/static/;
        expires 30d;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Мониторинг и логирование

### Просмотр логов
```bash
# Логи systemd сервиса
sudo journalctl -u pizzabot.service -f

# Логи приложения
tail -f logs/pizza_bot.log

# Проверка статуса сервиса
sudo systemctl status pizzabot.service
```

### Мониторинг ресурсов
```bash
# Использование CPU и памяти
top -p $(pgrep -f "python.*app.main")

# Размер базы данных
du -h pizza_store_bot.db

# Дисковое пространство
df -h
```

### Настройка алертов
Создайте скрипт для мониторинга:
```bash
#!/bin/bash
# check_bot.sh

SERVICE_NAME="pizzabot.service"

if ! systemctl is-active --quiet $SERVICE_NAME; then
    echo "Pizza Bot is down! Restarting..."
    systemctl restart $SERVICE_NAME
    # Отправка уведомления администратору
    curl -X POST "https://api.telegram.org/botYOUR_BOT_TOKEN/sendMessage" \
         -d "chat_id=ADMIN_CHAT_ID" \
         -d "text=🚨 Pizza Bot был перезапущен на сервере $(hostname)"
fi
```

Добавьте в cron:
```bash
crontab -e
# Проверка каждые 5 минут
*/5 * * * * /path/to/check_bot.sh
```

## Резервное копирование

### Скрипт резервного копирования
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/home/pizzabot/backups"
DB_PATH="/home/pizzabot/aiogram_pizza_bot/pizza_store_bot.db"
STATIC_DIR="/home/pizzabot/aiogram_pizza_bot/static"
DATE=$(date +%Y%m%d_%H%M%S)

# Создание резервной копии базы данных
cp $DB_PATH "$BACKUP_DIR/pizza_store_bot_$DATE.db"

# Создание архива статических файлов
tar -czf "$BACKUP_DIR/static_$DATE.tar.gz" -C $(dirname $STATIC_DIR) $(basename $STATIC_DIR)

# Удаление старых backup (старше 30 дней)
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

Настройка автоматического резервного копирования:
```bash
crontab -e
# Ежедневное резервное копирование в 2:00
0 2 * * * /home/pizzabot/backup.sh
```

### Восстановление из резервной копии
```bash
# Остановка сервиса
sudo systemctl stop pizzabot.service

# Восстановление базы данных
cp /home/pizzabot/backups/pizza_store_bot_YYYYMMDD_HHMMSS.db pizza_store_bot.db

# Восстановление статических файлов
tar -xzf /home/pizzabot/backups/static_YYYYMMDD_HHMMSS.tar.gz

# Запуск сервиса
sudo systemctl start pizzabot.service
```

## Решение проблем

### Бот не запускается
1. Проверьте токен бота:
   ```bash
   curl "https://api.telegram.org/botYOUR_TOKEN/getMe"
   ```

2. Проверьте путь к базе данных:
   ```bash
   ls -la pizza_store_bot.db
   ```

3. Проверьте права доступа:
   ```bash
   ls -la .env
   chmod 600 .env
   ```

### Ошибки базы данных
1. Проверьте миграции:
   ```bash
   alembic current
   alembic upgrade head
   ```

2. Пересоздание базы данных:
   ```bash
   rm pizza_store_bot.db
   python -c "import asyncio; from app.core.db import create_db; asyncio.run(create_db())"
   alembic upgrade head
   ```

### Проблемы с изображениями
1. Проверьте права доступа к директории static:
   ```bash
   chmod 755 static/
   chown -R pizzabot:pizzabot static/
   ```

2. Проверьте доступное место:
   ```bash
   df -h static/
   ```

### Высокая нагрузка
1. Оптимизация базы данных:
   ```sql
   VACUUM;
   ANALYZE;
   ```

2. Очистка старых записей корзины:
   ```sql
   DELETE FROM cart WHERE created_at < datetime('now', '-7 days');
   ```

3. Мониторинг медленных запросов

### Обновление бота
1. Создайте резервную копию
2. Остановите сервис:
   ```bash
   sudo systemctl stop pizzabot.service
   ```
3. Обновите код:
   ```bash
   git pull origin main
   pip install -r requirements.txt
   ```
4. Примените миграции:
   ```bash
   alembic upgrade head
   ```
5. Запустите сервис:
   ```bash
   sudo systemctl start pizzabot.service
   ```

## Контакты технической поддержки

При возникновении критических проблем обращайтесь к разработчику:
- Email: andrew.a.kobelev@yandex.ru
- Telegram: @andrew_kobelev (если доступен)

## Дополнительные ресурсы

- [Документация Aiogram](https://docs.aiogram.dev/)
- [Документация SQLAlchemy](https://docs.sqlalchemy.org/)
- [Документация Alembic](https://alembic.sqlalchemy.org/)
- [Telegram Bot API](https://core.telegram.org/bots/api)