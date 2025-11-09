# 🔍 Как найти таблицы в DBeaver

## Проблема

В DBeaver вы видите только "Databases", "Administer", "System info", но не видите таблиц.

## Решение: Где искать таблицы

### Шаг 1: Раскройте подключение

1. **В левой панели DBeaver найдите ваше подключение к PostgreSQL**
2. **Нажмите на стрелку** рядом с названием подключения (или двойной клик)
3. **Подключение раскроется**, и вы увидите:
   - 📁 **Databases** (Базы данных)
   - 📁 **Administer** (Администрирование)
   - 📁 **System info** (Системная информация)

### Шаг 2: Раскройте базу данных

1. **Раскройте "Databases"** (нажмите на стрелку)
2. **Вы увидите базу данных "railway"** (или другое имя, если вы его меняли)
3. **Раскройте "railway"** (нажмите на стрелку)

### Шаг 3: Раскройте схему "public"

1. **После раскрытия "railway" вы увидите:**
   - 📁 **Schemas** (Схемы)
   - 📁 **Extensions** (Расширения)
   - 📁 **Languages** (Языки)
   - И другие системные объекты

2. **Раскройте "Schemas"** (нажмите на стрелку)
3. **Вы увидите схему "public"**
4. **Раскройте "public"** (нажмите на стрелку)

### Шаг 4: Найдите таблицы

1. **После раскрытия "public" вы увидите:**
   - 📁 **Tables** (Таблицы)
   - 📁 **Views** (Представления)
   - 📁 **Functions** (Функции)
   - И другие объекты

2. **Раскройте "Tables"** (нажмите на стрелку)
3. **Здесь должны быть все ваши таблицы:**
   - `users`
   - `sessions`
   - `workout_days`
   - `exercises`
   - `sets`
   - `session_runs`
   - `performed_sets`

## Полный путь к таблицам:

```
Ваше подключение
  └── Databases
      └── railway
          └── Schemas
              └── public
                  └── Tables  ← ЗДЕСЬ ваши таблицы!
                      ├── users
                      ├── sessions
                      ├── workout_days
                      ├── exercises
                      ├── sets
                      ├── session_runs
                      └── performed_sets
```

## Если таблиц нет

### Вариант 1: Обновите список таблиц

1. **Правой кнопкой мыши на "Tables"**
2. **Выберите "Refresh" (Обновить)**
3. **Или нажмите `F5`**

### Вариант 2: Проверьте через SQL

1. **Откройте SQL Editor:**
   - Правой кнопкой мыши на подключение → **"SQL Editor"** → **"New SQL Script"**
   - Или нажмите `Ctrl+` (обратная кавычка)

2. **Выполните запрос:**
   ```sql
   SELECT table_name 
   FROM information_schema.tables 
   WHERE table_schema = 'public'
   ORDER BY table_name;
   ```

3. **Если таблиц нет:**
   - Таблицы будут созданы при первом использовании бота
   - Или создайте тестовую программу через бота
   - Или создайте таблицы вручную (см. инструкцию ниже)

### Вариант 3: Создайте таблицы через бота

1. **Откройте бота в Telegram**
2. **Добавьте тестовую программу:**
   - Нажмите "Мои Программы тренировок"
   - Выберите "Добавить программу"
   - Создайте простую программу (1 день, 1 упражнение)
   - Сохраните программу

3. **Обновите список таблиц в DBeaver:**
   - Правой кнопкой мыши на "Tables" → "Refresh"
   - Или нажмите `F5`

## Быстрая проверка через SQL

Выполните этот запрос в SQL Editor:

```sql
-- Проверка таблиц
SELECT 
    table_name,
    table_type
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY table_name;
```

**Если таблиц нет**, выполните:

```sql
-- Создание таблиц (выполните все запросы по очереди)
-- 1. Users
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_id INTEGER UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Sessions
CREATE TABLE IF NOT EXISTS sessions (
    session_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Workout Days
CREATE TABLE IF NOT EXISTS workout_days (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    day_index INTEGER NOT NULL,
    name VARCHAR NOT NULL
);

-- 4. Exercises
CREATE TABLE IF NOT EXISTS exercises (
    exercise_id SERIAL PRIMARY KEY,
    workout_day_id INTEGER NOT NULL REFERENCES workout_days(id) ON DELETE CASCADE,
    name VARCHAR NOT NULL,
    "order" INTEGER NOT NULL
);

-- 5. Sets
CREATE TABLE IF NOT EXISTS sets (
    set_id SERIAL PRIMARY KEY,
    exercise_id INTEGER NOT NULL REFERENCES exercises(exercise_id) ON DELETE CASCADE,
    set_index INTEGER NOT NULL,
    reps INTEGER NOT NULL,
    weight REAL
);

-- 6. Session Runs
CREATE TABLE IF NOT EXISTS session_runs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id INTEGER NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. Performed Sets
CREATE TABLE IF NOT EXISTS performed_sets (
    id SERIAL PRIMARY KEY,
    exercise_id INTEGER NOT NULL REFERENCES exercises(exercise_id) ON DELETE CASCADE,
    set_index INTEGER NOT NULL,
    weight REAL NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_run_id INTEGER NOT NULL REFERENCES session_runs(id) ON DELETE CASCADE
);

-- 8. Индексы
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_session_day ON workout_days(session_id, day_index);
CREATE INDEX IF NOT EXISTS idx_exercise_set ON sets(exercise_id, set_index);
CREATE INDEX IF NOT EXISTS idx_exercise_set_run ON performed_sets(exercise_id, set_index, session_run_id);
```

После выполнения запросов:
1. **Обновите список таблиц:** `F5`
2. **Таблицы должны появиться в "Tables"**

## Визуальная схема структуры

```
DBeaver Navigation Tree:
├── Ваше подключение (Railway PostgreSQL)
│   ├── Databases
│   │   └── railway
│   │       ├── Schemas
│   │       │   └── public  ← ВАЖНО: таблицы здесь!
│   │       │       ├── Tables  ← ЗДЕСЬ ваши таблицы
│   │       │       │   ├── users
│   │       │       │   ├── sessions
│   │       │       │   ├── workout_days
│   │       │       │   ├── exercises
│   │       │       │   ├── sets
│   │       │       │   ├── session_runs
│   │       │       │   └── performed_sets
│   │       │       ├── Views
│   │       │       └── Functions
│   │       ├── Extensions
│   │       └── Languages
│   ├── Administer
│   └── System info
```

## Полезные советы

1. **Используйте поиск:**
   - В DBeaver есть поиск (Ctrl+F)
   - Введите название таблицы (например, "users")
   - DBeaver найдет таблицу в дереве навигации

2. **Настройте фильтры:**
   - Правой кнопкой мыши на "Tables" → "Filter"
   - Вы можете фильтровать таблицы по имени

3. **Используйте SQL Editor:**
   - Быстрее выполнять SQL запросы, чем искать в дереве
   - `Ctrl+` (обратная кавычка) открывает SQL Editor

4. **Обновляйте список:**
   - Нажмите `F5` для обновления списка таблиц
   - Это особенно важно после создания новых таблиц

## ✅ Чек-лист

- [ ] Подключение к PostgreSQL работает
- [ ] Раскрыто "Databases" → "railway"
- [ ] Раскрыто "Schemas" → "public"
- [ ] Раскрыто "Tables"
- [ ] Видны таблицы: users, sessions, exercises и т.д.
- [ ] Если таблиц нет, обновлен список (F5)
- [ ] Если таблиц нет, создана тестовая программа через бота
- [ ] Если таблиц нет, созданы таблицы вручную через SQL

---

**Таблицы находятся в: Databases → railway → Schemas → public → Tables** 🎯

