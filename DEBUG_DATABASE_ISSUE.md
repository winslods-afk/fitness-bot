# Диагностика проблемы с потерей данных после деплоя

## Проблема

После деплоя на Railway программы тренировок удаляются, данные не сохраняются.

## Возможные причины

### 1. PostgreSQL не настроен, а Volume не создан

**Проверка:**
- В Railway Dashboard проверьте, есть ли PostgreSQL сервис
- Проверьте, есть ли переменная `DATABASE_URL` в Variables
- Проверьте, есть ли volume `/data`

**Решение:**
- **Вариант A (рекомендуется):** Добавьте PostgreSQL:
  - Railway Dashboard → "+ New" → "Database" → "Add PostgreSQL"
  - Railway автоматически создаст `DATABASE_URL`
  - Бот автоматически подключится к PostgreSQL
  - Данные будут сохраняться автоматически

- **Вариант B:** Настройте Volume для SQLite:
  ```bash
  railway service  # Выберите сервис "web"
  railway volume add --mount-path /data
  ```

### 2. Volume не привязан к сервису

**Проверка:**
```bash
railway volume list
```

Должен быть volume с mount path `/data`, привязанный к сервису `web`.

**Решение:**
```bash
railway volume add --mount-path /data
```

### 3. База данных создается не в том месте

**Проверка логов:**
После деплоя проверьте логи:
```bash
railway logs
```

Ищите сообщения:
- `Using SQLite on Railway: /data/fitness_bot.db` - ✅ правильно
- `Volume /data найден - данные будут сохраняться` - ✅ правильно
- `Volume /data НЕ найден` - ❌ проблема!

**Решение:**
- Убедитесь, что volume создан и привязан
- Перезапустите сервис через Railway Dashboard

### 4. Переменные окружения Railway не определяются

**Проверка:**
Проверьте логи при старте - должно быть:
```
Railway environment detected: True
```

Если `False`, значит Railway переменные не определяются.

**Решение:**
- Это нормально, если используется PostgreSQL (DATABASE_URL определяет окружение)
- Для SQLite убедитесь, что volume создан

## Пошаговая диагностика

### Шаг 1: Проверьте логи после деплоя

```bash
railway logs
```

Ищите сообщения:
- `Railway environment detected: True/False`
- `Data volume exists: True/False`
- `DATABASE_URL provided: True/False`
- `Using SQLite on Railway: ...` или `Using PostgreSQL database`
- `Volume /data найден` или `Volume /data НЕ найден`

### Шаг 2: Проверьте переменные окружения

```bash
railway variables
```

Должна быть переменная `DATABASE_URL` (если используется PostgreSQL) или ее не должно быть (если используется SQLite с volume).

### Шаг 3: Проверьте volume

```bash
railway volume list
```

Должен быть volume с mount path `/data`, привязанный к сервису `web`.

### Шаг 4: Проверьте базу данных

**Если используется PostgreSQL:**
- Подключитесь через DBeaver (см. [DBEAVER_RAILWAY_CONNECTION.md](DBEAVER_RAILWAY_CONNECTION.md))
- Проверьте, есть ли таблицы и данные

**Если используется SQLite:**
- Подключитесь через Railway CLI:
  ```bash
  railway connect
  ls -la /data
  ```
- Должен быть файл `fitness_bot.db` в `/data`

## Решение проблемы

### Решение 1: Использовать PostgreSQL (рекомендуется)

1. **Добавьте PostgreSQL в Railway:**
   - Railway Dashboard → "+ New" → "Database" → "Add PostgreSQL"
   - Railway автоматически создаст `DATABASE_URL`

2. **Проверьте деплой:**
   - Railway автоматически задеплоит изменения
   - В логах должно быть: `Using PostgreSQL database`
   - Данные будут сохраняться автоматически

3. **Проверьте данные:**
   - Добавьте тестовую программу через бота
   - Сделайте новый деплой
   - Проверьте, что программа осталась

### Решение 2: Настроить Volume для SQLite

1. **Создайте volume:**
   ```bash
   railway service  # Выберите сервис "web"
   railway volume add --mount-path /data
   ```

2. **Проверьте volume:**
   ```bash
   railway volume list
   ```
   Должен быть volume с mount path `/data`.

3. **Перезапустите сервис:**
   - Railway Dashboard → ваш сервис → "Settings" → "Restart"

4. **Проверьте логи:**
   ```bash
   railway logs
   ```
   Должно быть: `Volume /data найден - данные будут сохраняться`

5. **Проверьте данные:**
   - Добавьте тестовую программу через бота
   - Сделайте новый деплой
   - Проверьте, что программа осталась

## Проверка после исправления

1. **Добавьте тестовую программу:**
   - Откройте бота
   - Добавьте программу с 1 днем и 1 упражнением
   - Сохраните программу

2. **Сделайте новый деплой:**
   - Измените что-то в коде (например, README.md)
   - Закоммитьте и запушьте:
     ```bash
     git add README.md
     git commit -m "Test deploy"
     git push
     ```

3. **Проверьте данные:**
   - После деплоя откройте бота
   - Проверьте, что программа осталась
   - Если программа осталась - ✅ проблема решена!
   - Если программа удалилась - проверьте логи и volume/PostgreSQL

## Логи для отладки

После обновления кода в логах будут следующие сообщения:

**Для SQLite с volume:**
```
Railway environment detected: True
Data volume exists: True
DATABASE_URL provided: False
Using SQLite on Railway: /data/fitness_bot.db
✅ Volume /data найден - данные будут сохраняться
✅ База данных инициализирована
```

**Для PostgreSQL:**
```
Railway environment detected: True
Data volume exists: False
DATABASE_URL provided: True
Using PostgreSQL database
✅ База данных инициализирована
```

**Для SQLite БЕЗ volume (проблема!):**
```
Railway environment detected: True
Data volume exists: False
DATABASE_URL provided: False
Using SQLite on Railway: /data/fitness_bot.db
⚠️ Volume /data НЕ найден - данные могут теряться при деплое!
⚠️ Настройте volume: railway volume add --mount-path /data
✅ База данных инициализирована
```

## Рекомендация

**Используйте PostgreSQL** - это самое надежное решение:
- ✅ Автоматическое сохранение данных
- ✅ Не нужен volume
- ✅ Легкий доступ через DBeaver
- ✅ Автоматические бэкапы
- ✅ Масштабируемость

Подробнее: [RAILWAY_POSTGRESQL_SETUP.md](RAILWAY_POSTGRESQL_SETUP.md)

