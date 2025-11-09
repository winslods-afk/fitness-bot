# Подключение к базе данных Railway удаленно

## Быстрый ответ

**Да, можно!** Railway предоставляет PostgreSQL/MySQL как плагины, которые можно добавить к проекту. После добавления можно подключаться удаленно через различные инструменты.

## Шаг 1: Добавление PostgreSQL в Railway

### Через Railway Dashboard:

1. **Откройте ваш проект на Railway**
   - Перейдите на https://railway.app
   - Выберите ваш проект

2. **Добавьте PostgreSQL**
   - Нажмите **"+ New"** (или **"+ Add Service"**)
   - Выберите **"Database"** → **"Add PostgreSQL"**
   - Railway автоматически создаст PostgreSQL сервис

3. **Автоматическая настройка**
   - Railway автоматически создаст переменную `DATABASE_URL`
   - Эта переменная будет доступна всем сервисам в проекте
   - Ваш бот автоматически получит доступ к базе данных

### Через Railway CLI:

```bash
# Добавить PostgreSQL
railway add --plugin postgresql
```

## Шаг 2: Получение данных подключения

### Способ 1: Через Railway CLI

```bash
# Получить DATABASE_URL
railway variables

# Или получить конкретную переменную
railway variables get DATABASE_URL
```

### Способ 2: Через Railway Dashboard

1. Откройте ваш проект
2. Перейдите в сервис бота (web)
3. Откройте вкладку **"Variables"**
4. Найдите переменную `DATABASE_URL`
5. Скопируйте значение

Формат `DATABASE_URL`:
```
postgresql://user:password@host:port/database
```

## Шаг 3: Подключение к базе данных

### Вариант 1: Через Railway CLI (самый простой)

```bash
# Подключение к PostgreSQL через Railway CLI
railway connect postgres
```

Это откроет интерактивную сессию PostgreSQL, где вы можете выполнять SQL запросы.

### Вариант 2: Через DBeaver (визуальный интерфейс)

1. **Установите DBeaver:**
   - Скачайте с https://dbeaver.io/
   - Установите и запустите

2. **Получите DATABASE_URL:**
   ```bash
   railway variables get DATABASE_URL
   ```

3. **Парсинг DATABASE_URL:**
   - Формат: `postgresql://user:password@host:port/database`
   - **Host:** часть после `@` и до `:`
   - **Port:** часть после `:` и до `/`
   - **Database:** часть после `/`
   - **User:** часть после `//` и до `:`
   - **Password:** часть после `:` и до `@`

4. **Настройка DBeaver:**
   - Создайте новое подключение → **PostgreSQL**
   - Введите данные из `DATABASE_URL`:
     - **Host:** (из DATABASE_URL)
     - **Port:** (из DATABASE_URL)
     - **Database:** (из DATABASE_URL)
     - **Username:** (из DATABASE_URL)
     - **Password:** (из DATABASE_URL)
   - Нажмите **"Test Connection"**
   - Если подключение успешно, нажмите **"Finish"**

5. **Использование:**
   - Теперь вы можете просматривать таблицы, выполнять запросы, редактировать данные
   - Все изменения будут синхронизироваться с базой данных на Railway

### Вариант 3: Через pgAdmin

1. **Установите pgAdmin:**
   - Скачайте с https://www.pgadmin.org/
   - Установите и запустите

2. **Получите DATABASE_URL:**
   ```bash
   railway variables get DATABASE_URL
   ```

3. **Создайте новый сервер:**
   - Правый клик на **"Servers"** → **"Create"** → **"Server"**
   - Вкладка **"General"**: введите имя (например, "Railway")
   - Вкладка **"Connection"**: введите данные из `DATABASE_URL`
   - Нажмите **"Save"**

4. **Использование:**
   - Разверните сервер → **"Databases"** → ваша база данных
   - Просматривайте таблицы, выполняйте запросы

### Вариант 4: Через Python скрипт

```python
import os
import asyncpg
from urllib.parse import urlparse

# Получите DATABASE_URL из переменных окружения
# Или установите вручную:
# DATABASE_URL = "postgresql://user:password@host:port/database"
database_url = os.getenv("DATABASE_URL")

# Парсинг URL
parsed = urlparse(database_url)

# Подключение
async def connect_to_db():
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
    
    # Закрытие соединения
    await conn.close()

# Запуск
import asyncio
asyncio.run(connect_to_db())
```

### Вариант 5: Через psql (командная строка)

1. **Установите PostgreSQL client:**
   - Windows: https://www.postgresql.org/download/windows/
   - Mac: `brew install postgresql`
   - Linux: `sudo apt-get install postgresql-client`

2. **Получите DATABASE_URL:**
   ```bash
   railway variables get DATABASE_URL
   ```

3. **Подключение:**
   ```bash
   # Парсинг DATABASE_URL и подключение
   psql "postgresql://user:password@host:port/database"
   ```

4. **Выполнение запросов:**
   ```sql
   SELECT * FROM users;
   \dt  -- список таблиц
   \q   -- выход
   ```

## Шаг 4: Просмотр данных

После подключения вы можете:

1. **Просматривать таблицы:**
   ```sql
   SELECT * FROM users;
   SELECT * FROM sessions;
   SELECT * FROM exercises;
   SELECT * FROM performed_sets;
   ```

2. **Выполнять запросы:**
   ```sql
   -- Количество пользователей
   SELECT COUNT(*) FROM users;
   
   -- Программы пользователя
   SELECT s.name, s.created_at 
   FROM sessions s
   JOIN users u ON s.user_id = u.id
   WHERE u.telegram_id = 123456789;
   
   -- Статистика тренировок
   SELECT e.name, ps.weight, ps.timestamp
   FROM performed_sets ps
   JOIN exercises e ON ps.exercise_id = e.exercise_id
   ORDER BY ps.timestamp DESC
   LIMIT 10;
   ```

3. **Редактировать данные:**
   - Через DBeaver или pgAdmin можно редактировать данные визуально
   - Или через SQL запросы

## Важные замечания

- ✅ **DATABASE_URL автоматически доступен** всем сервисам в проекте
- ✅ **Подключение безопасно** - используется SSL
- ✅ **Данные сохраняются автоматически** - не нужен volume
- ✅ **Бесплатный тариф** включает PostgreSQL
- ⚠️ **Храните DATABASE_URL в секрете** - не публикуйте в открытом доступе
- ⚠️ **Резервное копирование** - Railway автоматически делает бэкапы

## Преимущества PostgreSQL на Railway

1. **Персистентное хранилище** - данные автоматически сохраняются
2. **Удаленный доступ** - можно подключаться извне
3. **Резервное копирование** - автоматические бэкапы
4. **Масштабируемость** - легко расширяется
5. **Бесплатный тариф** - Railway предоставляет PostgreSQL бесплатно
6. **Не нужен volume** - в отличие от SQLite

## Сравнение: SQLite (volume) vs PostgreSQL

### SQLite + Volume:
- ✅ Простота настройки
- ❌ Нужен volume для персистентности
- ❌ Сложнее удаленный доступ
- ❌ Ограниченная масштабируемость

### PostgreSQL (рекомендуется):
- ✅ Автоматическая персистентность
- ✅ Легкий удаленный доступ
- ✅ Масштабируемость
- ✅ Автоматические бэкапы
- ✅ Не нужен volume

## Рекомендация

Для продакшена рекомендуется использовать **PostgreSQL**, так как:
1. Не нужно настраивать volume
2. Легче подключаться удаленно
3. Автоматические бэкапы
4. Лучшая масштабируемость
5. Можно просматривать данные через DBeaver/pgAdmin

Подробная инструкция по настройке: [RAILWAY_POSTGRESQL_SETUP.md](RAILWAY_POSTGRESQL_SETUP.md)

