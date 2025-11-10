# Исправление ошибки 502 "Application failed to respond"

## Проблема

Railway возвращает ошибку 502, что означает, что приложение не запускается или не отвечает на запросы.

## Возможные причины и решения

### 1. Неправильная команда запуска в Procfile

**Проверьте файл `Procfile`:**

Если вы хотите запускать **только API**:
```
web: python api_server.py
```

Если вы хотите запускать **только бота**:
```
web: python -m app.main
```

Если вы хотите запускать **оба одновременно**, нужно использовать другой подход (см. ниже).

### 2. Приложение не слушает правильный порт

Railway автоматически устанавливает переменную окружения `PORT`. Убедитесь, что:

- API сервер использует `os.getenv("PORT")` (уже настроено в `api_server.py`)
- Приложение слушает на `0.0.0.0`, а не на `localhost` (уже настроено)

### 3. Приложение падает при запуске

**Проверьте логи Railway:**

1. Откройте Railway Dashboard
2. Выберите ваш сервис
3. Перейдите на вкладку **"Deployments"**
4. Откройте последний деплой
5. Посмотрите логи (вкладка **"Logs"**)

Ищите ошибки типа:
- `ModuleNotFoundError` - не установлены зависимости
- `ImportError` - проблемы с импортами
- `Database connection error` - проблемы с БД
- `Port already in use` - конфликт портов

### 4. Запуск API и бота одновременно

Если нужно запускать и API, и бота в одном сервисе, создайте файл `start_all.py`:

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

## Рекомендуемое решение: Отдельные сервисы

### Вариант 1: Только API (рекомендуется для тестирования endpoint)

1. Создайте новый сервис в Railway для API
2. В `Procfile` укажите:
   ```
   web: python api_server.py
   ```
3. Убедитесь, что переменная `DATABASE_URL` установлена
4. Деплойте

### Вариант 2: Только бот

1. В существующем сервисе бота в `Procfile` укажите:
   ```
   web: python -m app.main
   ```
2. Убедитесь, что переменная `TELEGRAM_BOT_TOKEN` установлена
3. Деплойте

### Вариант 3: Два отдельных сервиса

1. **Сервис 1 - Бот:**
   - `Procfile`: `web: python -m app.main`
   - Переменные: `TELEGRAM_BOT_TOKEN`, `DATABASE_URL`

2. **Сервис 2 - API:**
   - `Procfile`: `web: python api_server.py`
   - Переменные: `DATABASE_URL`

## Пошаговая диагностика

### Шаг 1: Проверьте Procfile

```bash
cat Procfile
```

Должно быть:
- Для API: `web: python api_server.py`
- Для бота: `web: python -m app.main`

### Шаг 2: Проверьте логи Railway

1. Railway Dashboard → Ваш сервис → Deployments → Последний деплой → Logs
2. Ищите ошибки в начале логов

### Шаг 3: Проверьте переменные окружения

В Railway Dashboard → Ваш сервис → Variables:

**Для API:**
- `DATABASE_URL` (обязательно)

**Для бота:**
- `TELEGRAM_BOT_TOKEN` (обязательно)
- `DATABASE_URL` (обязательно)

### Шаг 4: Проверьте, что порт правильный

В логах должно быть:
```
INFO:     Uvicorn running on http://0.0.0.0:XXXX
```

Где XXXX - порт из переменной `PORT` (Railway устанавливает автоматически).

### Шаг 5: Проверьте health endpoint

После деплоя попробуйте:
```bash
curl https://your-app.railway.app/health
```

Должен вернуть: `{"status": "ok"}`

## Быстрое исправление

1. **Создайте/обновите `Procfile`:**
   ```
   web: python api_server.py
   ```

2. **Убедитесь, что установлены зависимости:**
   Railway автоматически установит из `requirements.txt`

3. **Проверьте переменные окружения:**
   - `DATABASE_URL` должен быть установлен

4. **Редиплойте:**
   - Railway автоматически перезапустит при изменении `Procfile`
   - Или нажмите "Redeploy" вручную

## Проверка после исправления

1. Откройте логи Railway
2. Должны увидеть:
   ```
   INFO:     Started server process
   INFO:     Application startup complete.
   INFO:     Uvicorn running on http://0.0.0.0:XXXX
   ```

3. Проверьте health endpoint:
   ```bash
   curl https://your-app.railway.app/health
   ```

4. Проверьте основной endpoint:
   ```bash
   curl -H "X-API-Key: dotainstructor" https://your-app.railway.app/api/users
   ```

## Если проблема сохраняется

1. Проверьте логи Railway на наличие ошибок
2. Убедитесь, что база данных доступна (проверьте `DATABASE_URL`)
3. Попробуйте запустить локально: `python api_server.py`
4. Сравните локальные логи с логами Railway

