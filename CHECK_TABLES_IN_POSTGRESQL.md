# 🔍 Проверка таблиц в PostgreSQL

## Проблема

В DBeaver вы видите только "Databases", "Administer", "System info", но не видите таблиц.

## Решение

### Шаг 1: Проверьте схему "public"

1. **В DBeaver раскройте ваше подключение:**
   - Нажмите на стрелку рядом с подключением
   - Раскройте **"Databases"** → **"railway"**
   - Раскройте **"Schemas"**
   - Раскройте **"public"**
   - Раскройте **"Tables"**

2. **Если не видите схему "public":**
   - Правой кнопкой мыши на **"Schemas"** → **"Refresh"**
   - Или нажмите `F5` для обновления

### Шаг 2: Проверьте таблицы через SQL

1. **Откройте SQL Editor:**
   - Правой кнопкой мыши на подключение → **"SQL Editor"** → **"New SQL Script"
   - Или нажмите `Ctrl+` (обратная кавычка)

2. **Выполните запрос:**
   ```sql
   SELECT table_name 
   FROM information_schema.tables 
   WHERE table_schema = 'public'
   ORDER BY table_name;
   ```

3. **Если таблиц нет, вы увидите пустой результат**

### Шаг 3: Проверьте, что бот создал таблицы

1. **Проверьте логи Railway:**
   ```bash
   railway logs
   ```

2. **Ищите сообщения:**
   ```
   ✅ База данных инициализирована
   Таблицы проверены/созданы
   ```

3. **Если таблиц нет в логах:**
   - Бот может не создавать таблицы при первом запуске
   - Нужно перезапустить бота или дождаться первого использования

### Шаг 4: Создайте таблицы вручную (если нужно)

Если таблицы не созданы, вы можете создать их вручную через SQL:

1. **Откройте SQL Editor в DBeaver**

2. **Выполните SQL запросы для создания таблиц:**

```sql
-- Создание таблицы users
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_id INTEGER UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы sessions
CREATE TABLE IF NOT EXISTS sessions (
    session_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы workout_days
CREATE TABLE IF NOT EXISTS workout_days (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    day_index INTEGER NOT NULL,
    name VARCHAR NOT NULL
);

-- Создание таблицы exercises
CREATE TABLE IF NOT EXISTS exercises (
    exercise_id SERIAL PRIMARY KEY,
    workout_day_id INTEGER NOT NULL REFERENCES workout_days(id) ON DELETE CASCADE,
    name VARCHAR NOT NULL,
    "order" INTEGER NOT NULL
);

-- Создание таблицы sets
CREATE TABLE IF NOT EXISTS sets (
    set_id SERIAL PRIMARY KEY,
    exercise_id INTEGER NOT NULL REFERENCES exercises(exercise_id) ON DELETE CASCADE,
    set_index INTEGER NOT NULL,
    reps INTEGER NOT NULL,
    weight REAL
);

-- Создание таблицы session_runs
CREATE TABLE IF NOT EXISTS session_runs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id INTEGER NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы performed_sets
CREATE TABLE IF NOT EXISTS performed_sets (
    id SERIAL PRIMARY KEY,
    exercise_id INTEGER NOT NULL REFERENCES exercises(exercise_id) ON DELETE CASCADE,
    set_index INTEGER NOT NULL,
    weight REAL NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_run_id INTEGER NOT NULL REFERENCES session_runs(id) ON DELETE CASCADE
);

-- Создание индексов
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_session_day ON workout_days(session_id, day_index);
CREATE INDEX IF NOT EXISTS idx_exercise_set ON sets(exercise_id, set_index);
CREATE INDEX IF NOT EXISTS idx_exercise_set_run ON performed_sets(exercise_id, set_index, session_run_id);
```

3. **Выполните запросы:**
   - Нажмите `Ctrl+Enter` для выполнения
   - Или нажмите кнопку "Execute" (зеленая стрелка)

4. **Проверьте таблицы:**
   - Обновите список таблиц: `F5`
   - Или выполните запрос:
     ```sql
     SELECT table_name 
     FROM information_schema.tables 
     WHERE table_schema = 'public'
     ORDER BY table_name;
     ```

### Шаг 5: Проверьте настройки DBeaver

1. **Обновите список таблиц:**
   - Правой кнопкой мыши на **"Tables"** → **"Refresh"**
   - Или нажмите `F5`

2. **Проверьте фильтры:**
   - Правой кнопкой мыши на **"Tables"** → **"Filter"**
   - Убедитесь, что фильтры не скрывают таблицы

3. **Проверьте настройки подключения:**
   - Правой кнопкой мыши на подключение → **"Edit Connection"**
   - Вкладка **"Main"** → убедитесь, что база данных указана правильно: `railway`
   - Вкладка **"Filters"** → убедитесь, что фильтры не включены

## Альтернатива: Используйте Railway CLI

Если DBeaver не показывает таблицы, используйте Railway CLI:

```bash
# Подключитесь к PostgreSQL
railway connect postgres

# Проверьте таблицы
\dt

# Если таблиц нет, создайте их через бота:
# 1. Откройте бота в Telegram
# 2. Добавьте тестовую программу
# 3. Бот автоматически создаст таблицы при первом использовании
```

## Проверка через Python скрипт

Создайте файл `check_tables.py`:

```python
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def check_tables():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL не установлена")
        return
    
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif database_url.startswith("postgresql://"):
        if not database_url.startswith("postgresql+asyncpg://"):
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    try:
        engine = create_async_engine(database_url, echo=False)
        
        async with engine.begin() as conn:
            # Проверяем таблицы
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = result.fetchall()
            
            if tables:
                print(f"✅ Найдено таблиц: {len(tables)}")
                for table in tables:
                    print(f"  - {table[0]}")
            else:
                print("❌ Таблицы не найдены")
                print("💡 Таблицы будут созданы при первом использовании бота")
        
        await engine.dispose()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(check_tables())
```

Запустите скрипт:

```bash
# Установите DATABASE_URL
railway variables get DATABASE_URL

# Запустите скрипт
python check_tables.py
```

## Решение: Дождитесь первого использования бота

**Важно:** Таблицы могут создаваться не при старте бота, а при первом использовании!

1. **Откройте бота в Telegram**
2. **Добавьте тестовую программу:**
   - Нажмите "Мои Программы тренировок"
   - Выберите "Добавить программу"
   - Создайте простую программу (1 день, 1 упражнение)
   - Сохраните программу

3. **Проверьте таблицы в DBeaver:**
   - Обновите список таблиц: `F5`
   - Теперь должны появиться таблицы

## ✅ Чек-лист

- [ ] Подключение к PostgreSQL работает
- [ ] Раскрыта схема "public"
- [ ] Раскрыта папка "Tables"
- [ ] Выполнен SQL запрос для проверки таблиц
- [ ] Бот запущен и работает
- [ ] Создана тестовая программа через бота
- [ ] Таблицы обновлены в DBeaver (F5)

## ❓ Часто задаваемые вопросы

### Почему таблицы не видны сразу?

Таблицы могут создаваться не при старте бота, а при первом использовании. Это нормальное поведение SQLAlchemy.

### Как создать таблицы вручную?

Выполните SQL запросы из "Шаг 4" выше, или дождитесь первого использования бота.

### Как обновить список таблиц в DBeaver?

Нажмите `F5` или правой кнопкой мыши на "Tables" → "Refresh".

### Почему я вижу только "Databases", "Administer", "System info"?

Это нормально - это системные объекты PostgreSQL. Таблицы находятся в схеме "public" → "Tables".

---

**После выполнения этих шагов таблицы должны появиться!** 🎉

