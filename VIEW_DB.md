# 📊 Просмотр базы данных

Есть несколько способов посмотреть базу данных проекта:

## 🗄️ Где находится база данных

База данных SQLite находится в файле:
- **Локально:** `fitness_bot.db` (в корне проекта)
- **В Docker:** `/app/data/fitness_bot.db` (в папке `data`)

## 📋 Способы просмотра

### 1. Через Python скрипт (рекомендуется)

Запустите скрипт для просмотра данных:

```bash
cd C:\Users\Roman\fitness-bot
python view_db.py
```

Скрипт покажет:
- Всех пользователей
- Все программы с днями и упражнениями
- Последние тренировки с выполненными подходами
- Общую статистику

### 2. Через DB Browser for SQLite (визуальный редактор)

1. **Скачайте DB Browser:**
   - [sqlitebrowser.org](https://sqlitebrowser.org/)
   - Или через winget: `winget install DB Browser for SQLite`

2. **Откройте базу:**
   - Запустите DB Browser
   - File → Open Database
   - Выберите файл `fitness_bot.db` в папке проекта

3. **Просмотр данных:**
   - Вкладка "Browse Data" - просмотр таблиц
   - Вкладка "Execute SQL" - выполнение SQL запросов

### 3. Через командную строку (sqlite3)

Если у вас установлен sqlite3:

```bash
cd C:\Users\Roman\fitness-bot
sqlite3 fitness_bot.db
```

**Полезные команды:**
```sql
-- Показать все таблицы
.tables

-- Показать структуру таблицы
.schema users
.schema sessions

-- Просмотр данных
SELECT * FROM users;
SELECT * FROM sessions;
SELECT * FROM exercises;
SELECT * FROM performed_sets;

-- Выход
.quit
```

### 4. Через Python интерактивно

```bash
cd C:\Users\Roman\fitness-bot
python
```

```python
import asyncio
from app.db.init_db import async_session_maker
from app.db.models import User, Session
from sqlalchemy import select

async def view():
    async with async_session_maker() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        for user in users:
            print(f"User: {user.telegram_id}")

asyncio.run(view())
```

## 📊 Структура базы данных

### Таблицы:

1. **users** - пользователи бота
   - `id` - ID пользователя
   - `telegram_id` - Telegram ID
   - `created_at` - дата создания

2. **sessions** - программы тренировок
   - `session_id` - ID программы
   - `user_id` - ID пользователя
   - `name` - название программы
   - `created_at` - дата создания

3. **workout_days** - дни программы
   - `id` - ID дня
   - `session_id` - ID программы
   - `day_index` - номер дня (0, 1, 2...)
   - `name` - название дня

4. **exercises** - упражнения
   - `exercise_id` - ID упражнения
   - `workout_day_id` - ID дня
   - `name` - название упражнения
   - `order` - порядок в дне

5. **sets** - подходы (шаблоны)
   - `set_id` - ID подхода
   - `exercise_id` - ID упражнения
   - `set_index` - номер подхода
   - `reps` - количество повторений
   - `weight` - вес (опционально)

6. **session_runs** - запуски тренировок
   - `id` - ID запуска
   - `user_id` - ID пользователя
   - `session_id` - ID программы
   - `started_at` - время начала

7. **performed_sets** - выполненные подходы
   - `id` - ID записи
   - `exercise_id` - ID упражнения
   - `set_index` - номер подхода
   - `weight` - вес (кг)
   - `timestamp` - время выполнения
   - `session_run_id` - ID запуска тренировки

## 🔍 Полезные SQL запросы

### Показать все программы пользователя:
```sql
SELECT s.session_id, s.name, s.created_at
FROM sessions s
JOIN users u ON s.user_id = u.id
WHERE u.telegram_id = YOUR_TELEGRAM_ID;
```

### Показать упражнения программы:
```sql
SELECT e.name, e.order
FROM exercises e
JOIN workout_days wd ON e.workout_day_id = wd.id
WHERE wd.session_id = SESSION_ID
ORDER BY wd.day_index, e.order;
```

### Показать последние тренировки:
```sql
SELECT sr.id, s.name, sr.started_at
FROM session_runs sr
JOIN sessions s ON sr.session_id = s.session_id
ORDER BY sr.started_at DESC
LIMIT 10;
```

### Показать результаты тренировки:
```sql
SELECT e.name, ps.set_index, ps.weight, ps.timestamp
FROM performed_sets ps
JOIN exercises e ON ps.exercise_id = e.exercise_id
WHERE ps.session_run_id = RUN_ID
ORDER BY e.order, ps.set_index;
```

## 🛠️ Резервное копирование

### Создать бэкап:
```bash
# Windows
copy fitness_bot.db fitness_bot_backup.db

# Linux/Mac
cp fitness_bot.db fitness_bot_backup.db
```

### Восстановить из бэкапа:
```bash
# Windows
copy fitness_bot_backup.db fitness_bot.db

# Linux/Mac
cp fitness_bot_backup.db fitness_bot.db
```

## ⚠️ Важно

- **Не редактируйте базу данных напрямую** во время работы бота
- Делайте бэкапы перед изменениями
- Используйте скрипт `view_db.py` для безопасного просмотра

---

**Самый простой способ:** Запустите `python view_db.py` в папке проекта!

