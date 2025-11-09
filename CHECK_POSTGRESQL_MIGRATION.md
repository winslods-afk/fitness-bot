# ✅ Проверка миграции на PostgreSQL

## Шаг 1: Проверьте логи Railway

Проверьте логи вашего сервиса бота:

```bash
railway logs
```

Или через Railway Dashboard:
1. Откройте ваш проект на Railway
2. Выберите сервис бота (web)
3. Перейдите на вкладку "Deployments"
4. Нажмите на последний деплой
5. Просмотрите логи

### ✅ Что должно быть в логах:

```
DATABASE_URL provided: True
Using PostgreSQL database
Database type: PostgreSQL
✅ База данных инициализирована
```

### ❌ Если видите ошибки:

- `DATABASE_URL provided: False` - PostgreSQL не добавлен или переменная не создана
- `Using SQLite on Railway` - бот все еще использует SQLite
- Ошибки подключения - проверьте, что PostgreSQL сервис запущен

## Шаг 2: Проверьте переменные окружения

Проверьте, что переменная `DATABASE_URL` установлена:

```bash
railway variables get DATABASE_URL
```

Или через Railway Dashboard:
1. Откройте ваш проект на Railway
2. Выберите сервис бота (web)
3. Перейдите на вкладку "Variables"
4. Найдите переменную `DATABASE_URL`
5. Убедитесь, что она существует и содержит `postgresql://...`

## Шаг 3: Проверьте таблицы в PostgreSQL

### Способ 1: Через Railway CLI

```bash
# Подключитесь к PostgreSQL
railway connect postgres

# Выполните SQL запросы
\dt  # Показать все таблицы
SELECT * FROM users;
SELECT * FROM sessions;
SELECT * FROM exercises;
SELECT * FROM sets;
SELECT * FROM workout_days;
SELECT * FROM session_runs;
SELECT * FROM performed_sets;
```

### Способ 2: Через Railway Dashboard

1. Откройте ваш проект на Railway
2. Выберите сервис PostgreSQL
3. Перейдите на вкладку "Data"
4. Вы должны увидеть все таблицы:
   - `users`
   - `sessions`
   - `workout_days`
   - `exercises`
   - `sets`
   - `session_runs`
   - `performed_sets`

### Способ 3: Через Python скрипт

Создайте файл `check_postgres.py`:

```python
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def check_postgres():
    # Получите DATABASE_URL из переменных окружения
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL не установлена")
        return
    
    # Преобразуем postgres:// в postgresql+asyncpg://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    print(f"✅ Подключение к: {database_url.split('@')[0]}@***")
    
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
            
            print(f"\n✅ Найдено таблиц: {len(tables)}")
            for table in tables:
                print(f"  - {table[0]}")
            
            # Проверяем данные в таблицах
            print("\n📊 Данные в таблицах:")
            for table in tables:
                table_name = table[0]
                result = await conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = result.scalar()
                print(f"  - {table_name}: {count} записей")
        
        await engine.dispose()
        print("\n✅ Подключение к PostgreSQL работает!")
        
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")

if __name__ == "__main__":
    asyncio.run(check_postgres())
```

Запустите скрипт:

```bash
# Установите переменную DATABASE_URL
railway variables get DATABASE_URL > .env.postgres
# Или вручную добавьте DATABASE_URL в .env

# Запустите скрипт
python check_postgres.py
```

### Способ 4: Через DBeaver

1. Подключитесь к PostgreSQL через DBeaver
2. См. инструкцию: [DBEAVER_RAILWAY_CONNECTION.md](DBEAVER_RAILWAY_CONNECTION.md)
3. Проверьте таблицы в базе данных

## Шаг 4: Проверьте работу бота

1. **Откройте бота в Telegram**
2. **Добавьте тестовую программу:**
   - Нажмите "Мои Программы тренировок"
   - Выберите "Добавить программу"
   - Создайте простую программу (1 день, 1 упражнение)
   - Сохраните программу

3. **Проверьте данные в PostgreSQL:**
   ```bash
   railway connect postgres
   SELECT * FROM users;
   SELECT * FROM sessions;
   SELECT * FROM exercises;
   ```

4. **Сделайте тестовый деплой:**
   - Измените `README.md` (добавьте пробел)
   - Закоммитьте и запушьте:
     ```bash
     git add README.md
     git commit -m "Test PostgreSQL persistence"
     git push
     ```

5. **Проверьте данные после деплоя:**
   - После деплоя откройте бота
   - Проверьте, что программа осталась
   - ✅ Если программа осталась - **миграция успешна!**

## Шаг 5: Проверьте, что данные сохраняются

### Тест 1: Добавьте программу

1. Добавьте программу через бота
2. Проверьте в PostgreSQL:
   ```bash
   railway connect postgres
   SELECT * FROM sessions;
   SELECT * FROM workout_days;
   SELECT * FROM exercises;
   ```

### Тест 2: Сделайте деплой

1. Сделайте новый деплой (измените любой файл и запушьте)
2. После деплоя проверьте, что программа осталась
3. Проверьте в PostgreSQL:
   ```bash
   railway connect postgres
   SELECT * FROM sessions;
   ```

### Тест 3: Проведите тренировку

1. Начните тренировку через бота
2. Введите веса для подходов
3. Проверьте в PostgreSQL:
   ```bash
   railway connect postgres
   SELECT * FROM session_runs;
   SELECT * FROM performed_sets;
   ```

## ✅ Чек-лист проверки

- [ ] В логах: `Using PostgreSQL database`
- [ ] В логах: `✅ База данных инициализирована`
- [ ] Переменная `DATABASE_URL` установлена
- [ ] Все таблицы созданы в PostgreSQL
- [ ] Бот работает и отвечает на команды
- [ ] Программы сохраняются в PostgreSQL
- [ ] Программы сохраняются после деплоя
- [ ] Тренировки сохраняются в PostgreSQL

## ❓ Проблемы?

### Проблема: Бот все еще использует SQLite

**Решение:**
1. Проверьте, что PostgreSQL сервис создан и запущен
2. Проверьте, что переменная `DATABASE_URL` установлена
3. Перезапустите сервис бота через Railway Dashboard
4. Проверьте логи после перезапуска

### Проблема: Таблицы не созданы

**Решение:**
1. Проверьте логи - должны быть сообщения о создании таблиц
2. Убедитесь, что бот запущен и нет ошибок
3. Попробуйте перезапустить сервис бота

### Проблема: Данные не сохраняются

**Решение:**
1. Проверьте, что бот использует PostgreSQL (логи)
2. Проверьте, что PostgreSQL сервис запущен
3. Проверьте подключение через `railway connect postgres`

### Проблема: Ошибки подключения

**Решение:**
1. Проверьте, что PostgreSQL сервис создан и запущен
2. Проверьте переменную `DATABASE_URL`
3. Убедитесь, что `asyncpg` установлен (должен быть в `requirements.txt`)
4. Перезапустите сервис бота

## 📊 SQL запросы для проверки

### Проверить все таблицы:

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY table_name;
```

### Проверить количество записей:

```sql
SELECT 
    'users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'sessions', COUNT(*) FROM sessions
UNION ALL
SELECT 'workout_days', COUNT(*) FROM workout_days
UNION ALL
SELECT 'exercises', COUNT(*) FROM exercises
UNION ALL
SELECT 'sets', COUNT(*) FROM sets
UNION ALL
SELECT 'session_runs', COUNT(*) FROM session_runs
UNION ALL
SELECT 'performed_sets', COUNT(*) FROM performed_sets;
```

### Проверить последние программы:

```sql
SELECT 
    s.session_id,
    s.name as program_name,
    s.created_at,
    u.telegram_id
FROM sessions s
JOIN users u ON s.user_id = u.id
ORDER BY s.created_at DESC
LIMIT 10;
```

### Проверить последние тренировки:

```sql
SELECT 
    sr.id,
    sr.started_at,
    s.name as program_name,
    u.telegram_id,
    COUNT(ps.id) as sets_count
FROM session_runs sr
JOIN sessions s ON sr.session_id = s.session_id
JOIN users u ON sr.user_id = u.id
LEFT JOIN performed_sets ps ON ps.session_run_id = sr.id
GROUP BY sr.id, sr.started_at, s.name, u.telegram_id
ORDER BY sr.started_at DESC
LIMIT 10;
```

---

**Готово!** Если все проверки пройдены - миграция на PostgreSQL выполнена успешно! 🎉

