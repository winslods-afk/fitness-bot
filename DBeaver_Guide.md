# 📊 Просмотр базы данных в DBeaver

DBeaver - отличный инструмент для работы с базами данных. Вот как подключиться к базе данных проекта.

## 📥 Установка DBeaver

Если у вас еще не установлен DBeaver:

1. **Скачайте DBeaver:**
   - [dbeaver.io/download](https://dbeaver.io/download/)
   - Выберите Community Edition (бесплатная версия)

2. **Или через winget:**
   ```bash
   winget install DBeaver.DBeaver
   ```

## 🔌 Подключение к базе данных

### Шаг 1: Создание нового подключения

1. Запустите DBeaver
2. Нажмите на иконку **"New Database Connection"** (или `Ctrl+Shift+N`)
3. В списке баз данных выберите **SQLite**
4. Нажмите **Next**

### Шаг 2: Настройка подключения

1. В поле **Path** нажмите кнопку **Browse** (или введите путь вручную)
2. Найдите файл базы данных:
   ```
   C:\Users\Roman\fitness-bot\fitness_bot.db
   ```
3. Нажмите **Test Connection** для проверки
4. Если все ок, нажмите **Finish**

### Шаг 3: Просмотр данных

После подключения вы увидите структуру базы данных в левой панели:

```
📁 fitness_bot
  📁 Tables
    📄 users
    📄 sessions
    📄 workout_days
    📄 exercises
    📄 sets
    📄 session_runs
    📄 performed_sets
```

## 📋 Просмотр таблиц

### Способ 1: Двойной клик

1. Раскройте папку **Tables**
2. Дважды кликните на таблицу (например, `users`)
3. Данные откроются во вкладке

### Способ 2: Контекстное меню

1. Правый клик на таблице
2. Выберите **View Data** → **All Rows**

## 🔍 Полезные SQL запросы

Откройте SQL редактор: `Ctrl+\` или кнопка **SQL Editor**

### Показать всех пользователей:
```sql
SELECT * FROM users;
```

### Показать все программы:
```sql
SELECT 
    s.session_id,
    s.name AS program_name,
    u.telegram_id,
    s.created_at
FROM sessions s
JOIN users u ON s.user_id = u.id
ORDER BY s.created_at DESC;
```

### Показать упражнения программы:
```sql
SELECT 
    wd.name AS day_name,
    e.name AS exercise_name,
    COUNT(st.set_id) AS sets_count
FROM exercises e
JOIN workout_days wd ON e.workout_day_id = wd.id
LEFT JOIN sets st ON st.exercise_id = e.exercise_id
WHERE wd.session_id = 1  -- Замените на ID вашей программы
GROUP BY e.exercise_id
ORDER BY wd.day_index, e.order;
```

### Показать последние тренировки:
```sql
SELECT 
    sr.id AS run_id,
    s.name AS program_name,
    u.telegram_id,
    sr.started_at,
    COUNT(ps.id) AS sets_count
FROM session_runs sr
JOIN sessions s ON sr.session_id = s.session_id
JOIN users u ON sr.user_id = u.id
LEFT JOIN performed_sets ps ON ps.session_run_id = sr.id
GROUP BY sr.id
ORDER BY sr.started_at DESC
LIMIT 10;
```

### Показать результаты конкретной тренировки:
```sql
SELECT 
    e.name AS exercise_name,
    ps.set_index,
    ps.weight,
    ps.timestamp
FROM performed_sets ps
JOIN exercises e ON ps.exercise_id = e.exercise_id
WHERE ps.session_run_id = 1  -- Замените на ID тренировки
ORDER BY e.order, ps.set_index;
```

### Статистика по пользователю:
```sql
SELECT 
    u.telegram_id,
    COUNT(DISTINCT s.session_id) AS programs_count,
    COUNT(DISTINCT sr.id) AS workouts_count,
    COUNT(ps.id) AS total_sets
FROM users u
LEFT JOIN sessions s ON s.user_id = u.id
LEFT JOIN session_runs sr ON sr.user_id = u.id
LEFT JOIN performed_sets ps ON ps.session_run_id = sr.id
GROUP BY u.id;
```

## 🎨 Полезные функции DBeaver

### 1. Экспорт данных

1. Правый клик на таблице → **Export Data**
2. Выберите формат (CSV, Excel, JSON и т.д.)
3. Настройте параметры и экспортируйте

### 2. Редактирование данных

1. Откройте таблицу
2. Дважды кликните на ячейку для редактирования
3. Сохраните изменения (`Ctrl+S`)

⚠️ **Внимание:** Будьте осторожны при редактировании данных напрямую!

### 3. Создание диаграмм

1. Правый клик на базе данных → **View Diagram**
2. DBeaver автоматически создаст ER-диаграмму

### 4. Поиск по базе

1. `Ctrl+Shift+F` - поиск по всей базе данных
2. Введите текст для поиска
3. Выберите таблицы для поиска

## 🔧 Настройки для удобства

### Изменить тему:
1. Window → Preferences → Appearance → Theme
2. Выберите Dark или Light тему

### Настройка SQL редактора:
1. Window → Preferences → Editors → SQL Editor
2. Настройте подсветку синтаксиса, автодополнение и т.д.

### Показывать количество записей:
1. Правый клик на таблице → Properties
2. Включите "Show row count"

## 📊 Структура таблиц

### users
- `id` (INTEGER, PRIMARY KEY)
- `telegram_id` (INTEGER, UNIQUE)
- `created_at` (DATETIME)

### sessions
- `session_id` (INTEGER, PRIMARY KEY)
- `user_id` (INTEGER, FOREIGN KEY → users.id)
- `name` (TEXT)
- `created_at` (DATETIME)

### workout_days
- `id` (INTEGER, PRIMARY KEY)
- `session_id` (INTEGER, FOREIGN KEY → sessions.session_id)
- `day_index` (INTEGER)
- `name` (TEXT)

### exercises
- `exercise_id` (INTEGER, PRIMARY KEY)
- `workout_day_id` (INTEGER, FOREIGN KEY → workout_days.id)
- `name` (TEXT)
- `order` (INTEGER)

### sets
- `set_id` (INTEGER, PRIMARY KEY)
- `exercise_id` (INTEGER, FOREIGN KEY → exercises.exercise_id)
- `set_index` (INTEGER)
- `reps` (INTEGER)
- `weight` (REAL, nullable)

### session_runs
- `id` (INTEGER, PRIMARY KEY)
- `user_id` (INTEGER, FOREIGN KEY → users.id)
- `session_id` (INTEGER, FOREIGN KEY → sessions.session_id)
- `started_at` (DATETIME)

### performed_sets
- `id` (INTEGER, PRIMARY KEY)
- `exercise_id` (INTEGER, FOREIGN KEY → exercises.exercise_id)
- `set_index` (INTEGER)
- `weight` (REAL)
- `timestamp` (DATETIME)
- `session_run_id` (INTEGER, FOREIGN KEY → session_runs.id)

## 💡 Советы

1. **Используйте закладки** для часто используемых запросов
2. **Сохраняйте SQL скрипты** для повторного использования
3. **Делайте бэкапы** перед изменениями данных
4. **Используйте транзакции** при массовых изменениях

## ⚠️ Важно

- **Не редактируйте базу данных** во время работы бота
- **Делайте бэкапы** перед изменениями
- **Используйте транзакции** для безопасных изменений

---

**Готово!** Теперь вы можете просматривать и анализировать базу данных в DBeaver.

