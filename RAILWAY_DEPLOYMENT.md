# Развертывание на Railway

## Настройка Procfile

Railway использует файл `Procfile` для определения команды запуска.

### Для API сервера (рекомендуется для API endpoints):

```
web: python api_server.py
```

### Для бота:

```
web: python -m app.main
```

### Для запуска обоих одновременно:

Создайте файл `start_all.py`:

```python
"""Запуск бота и API одновременно."""
import asyncio
import logging
import uvicorn
from multiprocessing import Process
from app.main import main as bot_main
from app.db.init_db import init_db
from app.api.main import app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def run_api():
    """Запуск API сервера."""
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app.api.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )


async def run_bot():
    """Запуск бота."""
    await init_db()
    await bot_main()


if __name__ == "__main__":
    # Инициализация БД
    asyncio.run(init_db())
    
    # Запуск API в отдельном процессе
    api_process = Process(target=run_api)
    api_process.start()
    
    # Запуск бота в основном процессе
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.info("Остановка...")
        api_process.terminate()
        api_process.join()
```

И в `Procfile`:
```
web: python start_all.py
```

**⚠️ Внимание:** Railway рекомендует запускать API и бота в **отдельных сервисах**.

## Рекомендуемая конфигурация: Два сервиса

### Сервис 1 - Бот
- `Procfile`: `web: python -m app.main`
- Переменные окружения:
  - `TELEGRAM_BOT_TOKEN` (обязательно)
  - `DATABASE_URL` (обязательно)

### Сервис 2 - API
- `Procfile`: `web: python api_server.py`
- Переменные окружения:
  - `DATABASE_URL` (обязательно)
  - `PORT` (устанавливается автоматически Railway)

## Проверка после деплоя

1. **Проверьте логи Railway:**
   - Dashboard → Ваш сервис → Deployments → Последний деплой → Logs
   - Для API должны увидеть: `INFO: Uvicorn running on http://0.0.0.0:XXXX`
   - Для бота должны увидеть: `INFO: Бот запущен и готов к работе`

2. **Проверьте health endpoint (для API):**
   ```bash
   curl https://your-api.railway.app/health
   ```
   Должен вернуть: `{"status": "ok"}`

3. **Проверьте основной endpoint (для API):**
   ```bash
   curl -H "X-API-Key: dotainstructor" https://your-api.railway.app/api/users
   ```

## Устранение проблем

### Ошибка 502 "Application failed to respond"

**Причины:**
1. Неправильная команда в `Procfile`
2. Приложение падает при запуске
3. Неправильный порт

**Решение:**
1. Проверьте `Procfile` - должна быть правильная команда
2. Проверьте логи Railway на наличие ошибок
3. Убедитесь, что переменные окружения установлены

### Приложение не запускается

**Проверьте:**
1. Логи Railway на наличие ошибок импорта
2. Установлены ли все зависимости (`requirements.txt`)
3. Правильно ли настроена база данных (`DATABASE_URL`)

### База данных не подключается

**Проверьте:**
1. Переменная `DATABASE_URL` установлена в Railway
2. PostgreSQL сервис запущен и подключен
3. Формат `DATABASE_URL` правильный (начинается с `postgresql+asyncpg://`)

