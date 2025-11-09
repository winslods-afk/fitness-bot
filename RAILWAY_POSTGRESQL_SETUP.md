# Настройка PostgreSQL на Railway

## Преимущества PostgreSQL на Railway

- ✅ **Персистентное хранилище** - данные автоматически сохраняются
- ✅ **Удаленный доступ** - можно подключаться извне
- ✅ **Резервное копирование** - автоматические бэкапы
- ✅ **Масштабируемость** - легко расширяется
- ✅ **Бесплатный тариф** - Railway предоставляет PostgreSQL бесплатно

## Шаг 1: Добавление PostgreSQL в проект

### Через Railway Dashboard:

1. **Откройте ваш проект на Railway**
   - Перейдите на https://railway.app
   - Выберите ваш проект

2. **Добавьте PostgreSQL сервис**
   - Нажмите **"+ New"** → **"Database"** → **"Add PostgreSQL"**
   - Railway автоматически создаст PostgreSQL сервис

3. **Получите переменные окружения**
   - После создания PostgreSQL, Railway автоматически создаст переменную `DATABASE_URL`
   - Перейдите в ваш сервис бота (web) → **"Variables"**
   - Вы увидите переменную `DATABASE_URL` (она уже доступна для всех сервисов в проекте)

### Через Railway CLI:

```bash
# Добавить PostgreSQL
railway add --plugin postgresql
```

## Шаг 2: Обновление конфигурации приложения

После добавления PostgreSQL, обновите `app/config.py`:

```python
"""Конфигурация бота."""
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не установлен в переменных окружения")

# База данных
# Railway автоматически предоставляет DATABASE_URL для PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Fallback на SQLite для локальной разработки
    if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY"):
        # Railway deployment - используем персистентное хранилище для SQLite
        DB_DIR = "/data"
        os.makedirs(DB_DIR, exist_ok=True)
        DB_PATH = os.path.join(DB_DIR, "fitness_bot.db")
        DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"
    else:
        # Локальная разработка
        DB_PATH = os.getenv("DATABASE_PATH", "fitness_bot.db")
        DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"
else:
    # Если DATABASE_URL предоставлен (PostgreSQL), используем его
    # Преобразуем postgres:// в postgresql+asyncpg:// для SQLAlchemy async
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
    elif DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
```

## Шаг 3: Обновление зависимостей

Добавьте `asyncpg` в `requirements.txt`:

```
asyncpg==0.29.0
```

Или установите локально:

```bash
pip install asyncpg
```

## Шаг 4: Обновление инициализации БД

`app/db/init_db.py` уже поддерживает любую базу данных через `DATABASE_URL`, поэтому изменения не требуются.

## Шаг 5: Деплой

```bash
git add .
git commit -m "Add PostgreSQL support"
git push
```

Railway автоматически задеплоит изменения.

## Подключение к PostgreSQL удаленно

### Способ 1: Через Railway CLI

```bash
# Подключение к PostgreSQL через Railway CLI
railway connect postgres
```

Это откроет интерактивную сессию PostgreSQL.

### Способ 2: Получение данных подключения

```bash
# Получить DATABASE_URL
railway variables

# Или получить конкретную переменную
railway variables get DATABASE_URL
```

Формат `DATABASE_URL`:
```
postgresql://user:password@host:port/database
```

### Способ 3: Использование внешних инструментов

#### DBeaver:

1. **Получите данные подключения:**
   ```bash
   railway variables get DATABASE_URL
   ```

2. **Парсинг DATABASE_URL:**
   - `postgresql://user:password@host:port/database`
   - Host: часть после `@` и до `:`
   - Port: часть после `:` и до `/`
   - Database: часть после `/`
   - User: часть после `//` и до `:`
   - Password: часть после `:` и до `@`

3. **Настройка DBeaver:**
   - Создайте новое подключение PostgreSQL
   - Введите данные из `DATABASE_URL`
   - Проверьте подключение

#### pgAdmin:

1. Получите `DATABASE_URL` через Railway CLI
2. Используйте данные для создания нового сервера в pgAdmin
3. Подключитесь к базе данных

#### Python скрипт:

```python
import os
import asyncpg
from urllib.parse import urlparse

# Получите DATABASE_URL из переменных окружения
database_url = os.getenv("DATABASE_URL")

# Парсинг URL
parsed = urlparse(database_url)

# Подключение
conn = await asyncpg.connect(
    host=parsed.hostname,
    port=parsed.port,
    user=parsed.username,
    password=parsed.password,
    database=parsed.path[1:]  # Убираем ведущий /
)

# Выполнение запросов
rows = await conn.fetch("SELECT * FROM users")
for row in rows:
    print(row)
```

## Проверка подключения

После деплоя проверьте логи:

```bash
railway logs
```

Должно быть:
```
База данных инициализирована
```

## Миграция данных из SQLite в PostgreSQL

Если у вас уже есть данные в SQLite:

1. **Экспортируйте данные из SQLite:**
   ```bash
   # Используйте команду бота /export_db
   # Или используйте sqlite3 для экспорта
   sqlite3 fitness_bot.db .dump > backup.sql
   ```

2. **Импортируйте в PostgreSQL:**
   - Используйте инструменты миграции
   - Или создайте скрипт для переноса данных

## Важные замечания

- ✅ **PostgreSQL автоматически создается** при добавлении сервиса
- ✅ **DATABASE_URL автоматически доступен** всем сервисам в проекте
- ✅ **Данные сохраняются автоматически** - не нужен volume
- ✅ **Бесплатный тариф** включает PostgreSQL
- ⚠️ **Локальная разработка** - используйте SQLite (fallback в config.py)
- ⚠️ **Миграция схемы** - таблицы создаются автоматически при первом запуске

## Сравнение: SQLite vs PostgreSQL

### SQLite (текущее решение):
- ✅ Простота настройки
- ✅ Не требует отдельного сервиса
- ❌ Нужен volume для персистентности
- ❌ Сложнее удаленный доступ
- ❌ Ограниченная масштабируемость

### PostgreSQL (рекомендуется):
- ✅ Автоматическая персистентность
- ✅ Легкий удаленный доступ
- ✅ Масштабируемость
- ✅ Автоматические бэкапы
- ❌ Требует отдельный сервис (но Railway предоставляет бесплатно)

## Рекомендация

Для продакшена рекомендуется использовать **PostgreSQL**, так как:
1. Не нужно настраивать volume
2. Легче подключаться удаленно
3. Автоматические бэкапы
4. Лучшая масштабируемость

Для локальной разработки можно продолжать использовать SQLite.

