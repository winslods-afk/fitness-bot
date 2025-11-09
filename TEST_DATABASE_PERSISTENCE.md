# Тестирование сохранения базы данных

## Проблема

После деплоя программы тренировок удаляются, даже если volume настроен.

## Диагностика

### Шаг 1: Проверьте логи после деплоя

После следующего деплоя проверьте логи:

```bash
railway logs
```

Ищите следующие сообщения:

**Должно быть:**
```
============================================================
DATABASE CONFIGURATION
============================================================
Railway environment detected: True
Data volume exists: True
DATABASE_URL provided: False
Using SQLite on Railway: /data/fitness_bot.db
Database type: SQLite
SQLite database path: /data/fitness_bot.db
Database file exists: False/True
Directory exists: True
Directory writable: True
✅ Volume /data найден - данные будут сохраняться
✅ Директория /data доступна для записи
✅ База данных создана: /data/fitness_bot.db (размер: XXX байт)
```

**Если видите:**
```
Data volume exists: False
⚠️ Volume /data НЕ найден - данные могут теряться при деплое!
```

Тогда volume не настроен правильно.

### Шаг 2: Проверьте volume через Railway CLI

```bash
railway volume list
```

Должен быть volume с:
- Mount path: `/data`
- Attached to: `web` (или имя вашего сервиса)

### Шаг 3: Проверьте базу данных через Railway CLI

```bash
# Подключитесь к контейнеру
railway run bash

# Проверьте, существует ли файл базы данных
ls -la /data/fitness_bot.db

# Проверьте размер файла
du -h /data/fitness_bot.db

# Проверьте содержимое директории
ls -la /data/
```

### Шаг 4: Проверьте данные в базе данных

```bash
# Подключитесь к контейнеру
railway run bash

# Используйте sqlite3 для проверки данных
sqlite3 /data/fitness_bot.db "SELECT * FROM users;"
sqlite3 /data/fitness_bot.db "SELECT * FROM sessions;"
```

## Возможные проблемы и решения

### Проблема 1: Volume не монтируется

**Симптомы:**
- В логах: `Data volume exists: False`
- `Directory /data does not exist!`

**Решение:**
1. Проверьте, что volume создан:
   ```bash
   railway volume list
   ```

2. Если volume нет, создайте его:
   ```bash
   railway service  # Выберите сервис "web"
   railway volume add --mount-path /data
   ```

3. Перезапустите сервис через Railway Dashboard

### Проблема 2: Volume монтируется, но база данных не сохраняется

**Симптомы:**
- В логах: `Data volume exists: True`
- Но данные все равно теряются после деплоя

**Возможные причины:**

1. **База данных создается не в том месте:**
   - Проверьте логи: `SQLite database path: /data/fitness_bot.db`
   - Если путь другой - проблема в конфигурации

2. **Volume монтируется после создания базы данных:**
   - Railway может монтировать volume после старта контейнера
   - Но это маловероятно, так как volume монтируется при создании контейнера

3. **База данных создается, но теряется при пересоздании контейнера:**
   - Если volume не привязан правильно, данные могут теряться
   - Проверьте, что volume привязан к сервису

### Проблема 3: База данных существует, но данные не сохраняются

**Симптомы:**
- Файл базы данных существует в `/data/fitness_bot.db`
- Но данные (программы) не сохраняются

**Возможные причины:**

1. **База данных пересоздается при каждом деплое:**
   - SQLAlchemy может пересоздавать таблицы
   - Но данные должны сохраняться, если файл существует

2. **Проблема с транзакциями:**
   - Данные не коммитятся в базу данных
   - Но это маловероятно, так как код использует правильные транзакции

3. **Разные файлы базы данных:**
   - База данных создается в одном месте, а читается из другого
   - Но это маловероятно, так как путь фиксированный

## Решение: Использовать PostgreSQL

**Самое надежное решение - использовать PostgreSQL:**

1. **Добавьте PostgreSQL в Railway:**
   - Railway Dashboard → "+ New" → "Database" → "Add PostgreSQL"
   - Railway автоматически создаст `DATABASE_URL`

2. **Проверьте деплой:**
   - После деплоя в логах должно быть: `Using PostgreSQL database`
   - Данные будут сохраняться автоматически

3. **Проверьте данные:**
   - Добавьте тестовую программу
   - Сделайте новый деплой
   - Программа должна остаться

**Преимущества PostgreSQL:**
- ✅ Автоматическое сохранение данных
- ✅ Не нужен volume
- ✅ Легкий доступ через DBeaver
- ✅ Автоматические бэкапы
- ✅ Масштабируемость

## Альтернативное решение: Проверить volume вручную

Если хотите использовать SQLite с volume:

1. **Подключитесь к контейнеру:**
   ```bash
   railway run bash
   ```

2. **Проверьте volume:**
   ```bash
   ls -la /data
   cat /data/fitness_bot.db  # Должен быть файл (бинарный)
   ```

3. **Добавьте тестовые данные:**
   ```bash
   sqlite3 /data/fitness_bot.db "INSERT INTO users (telegram_id, created_at) VALUES (999999999, datetime('now'));"
   ```

4. **Сделайте новый деплой:**
   - Измените что-то в коде
   - Закоммитьте и запушьте

5. **Проверьте данные после деплоя:**
   ```bash
   railway run bash
   sqlite3 /data/fitness_bot.db "SELECT * FROM users WHERE telegram_id = 999999999;"
   ```

Если данные сохранились - volume работает правильно.
Если данные потерялись - volume не работает, используйте PostgreSQL.

## Рекомендация

**Используйте PostgreSQL** - это самое надежное решение для продакшена.

Подробнее: [RAILWAY_POSTGRESQL_SETUP.md](RAILWAY_POSTGRESQL_SETUP.md)

