# ⚠️ СРОЧНОЕ РЕШЕНИЕ: Потеря данных после деплоя

## Проблема

После каждого деплоя все программы тренировок удаляются, даже если volume настроен.

## Причина

**SQLite с volume на Railway может терять данные**, потому что:
1. Volume может монтироваться неправильно
2. База данных может создаваться не в том месте
3. Railway может пересоздавать контейнер и терять данные

## ✅ РЕШЕНИЕ: Используйте PostgreSQL

**Это самое надежное решение - PostgreSQL сохраняет данные автоматически!**

### Шаг 1: Добавьте PostgreSQL (5 минут)

1. **Откройте Railway Dashboard:**
   - https://railway.app
   - Выберите ваш проект

2. **Добавьте PostgreSQL:**
   - Нажмите **"+ New"** → **"Database"** → **"Add PostgreSQL"**
   - Railway автоматически создаст PostgreSQL сервис
   - Railway автоматически добавит переменную `DATABASE_URL` в ваш сервис бота

3. **Перезапустите сервис:**
   - Railway автоматически перезапустит сервис после добавления PostgreSQL
   - Или вручную: Railway Dashboard → ваш сервис → "Settings" → "Restart"

### Шаг 2: Проверьте логи

После перезапуска проверьте логи:

```bash
railway logs
```

Должно быть:
```
DATABASE_URL provided: True
Using PostgreSQL database
✅ База данных инициализирована
```

### Шаг 3: Проверьте данные

1. **Добавьте тестовую программу:**
   - Откройте бота
   - Добавьте программу с 1 днем и 1 упражнением
   - Сохраните программу

2. **Сделайте новый деплой:**
   - Измените что-то в коде (например, README.md)
   - Закоммитьте и запушьте:
     ```bash
     git add README.md
     git commit -m "Test deploy with PostgreSQL"
     git push
     ```

3. **Проверьте данные:**
   - После деплоя откройте бота
   - Проверьте, что программа осталась
   - ✅ Если программа осталась - проблема решена!

## Почему PostgreSQL лучше?

- ✅ **Автоматическое сохранение данных** - данные сохраняются между деплоями
- ✅ **Не нужен volume** - PostgreSQL работает отдельным сервисом
- ✅ **Автоматические бэкапы** - Railway делает бэкапы автоматически
- ✅ **Легкий доступ** - можно подключиться через DBeaver
- ✅ **Масштабируемость** - можно масштабировать при необходимости

## Альтернатива: Проверьте volume для SQLite

Если вы хотите использовать SQLite с volume:

### Проверьте volume:

```bash
railway volume list
```

Должен быть volume с:
- Mount path: `/data`
- Attached to: `web` (или имя вашего сервиса)

### Проверьте базу данных:

```bash
# Подключитесь к контейнеру
railway run bash

# Проверьте, существует ли файл базы данных
ls -la /data/fitness_bot.db

# Проверьте данные
sqlite3 /data/fitness_bot.db "SELECT * FROM users;"
sqlite3 /data/fitness_bot.db "SELECT * FROM sessions;"
```

### Проверьте логи после деплоя:

После следующего деплоя проверьте логи - должны быть:

```
Volume /data check: exists=True, writable=True
✅ Using SQLite on Railway: /data/fitness_bot.db
✅ Volume /data настроен правильно - данные будут сохраняться
✅ База данных: /data/fitness_bot.db (размер: XXX байт)
✅ База данных находится в volume /data - данные сохраняются
```

Если видите ошибки - используйте PostgreSQL!

## Рекомендация

**Используйте PostgreSQL** - это самое надежное решение для продакшена. SQLite с volume может работать, но PostgreSQL гарантирует сохранность данных.

## Дополнительная помощь

- См. [FIX_DATA_LOSS.md](FIX_DATA_LOSS.md) для подробной инструкции
- См. [RAILWAY_POSTGRESQL_SETUP.md](RAILWAY_POSTGRESQL_SETUP.md) для настройки PostgreSQL
- См. [DBEAVER_RAILWAY_CONNECTION.md](DBEAVER_RAILWAY_CONNECTION.md) для подключения через DBeaver

