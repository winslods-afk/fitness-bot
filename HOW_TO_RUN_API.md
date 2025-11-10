# Как запустить и вызвать API endpoint

## Шаг 1: Установка зависимостей

Убедитесь, что установлены все зависимости:

```bash
pip install -r requirements.txt
```

Или если используете виртуальное окружение:

```bash
# Создать виртуальное окружение (если еще не создано)
python -m venv venv

# Активировать виртуальное окружение
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt
```

## Шаг 2: Запуск API сервера

Запустите API сервер:

```bash
python api_server.py
```

Вы должны увидеть что-то вроде:

```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Инициализация базы данных для API...
INFO:     База данных инициализирована
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

✅ **API сервер запущен и доступен на `http://localhost:8000`**

## Шаг 3: Вызов endpoint

### Вариант 1: Postman (рекомендуется)

1. **Импортируйте коллекцию:**
   - Откройте Postman
   - Нажмите **Import** (левый верхний угол)
   - Выберите файл `Fitness_Bot_API.postman_collection.json`
   - Нажмите **Import**

2. **Импортируйте окружение (опционально):**
   - Нажмите **Import** снова
   - Выберите файл `Fitness_Bot_API.postman_environment.json`
   - Выберите окружение "Fitness Bot API - Local" в правом верхнем углу

3. **Отправьте запрос:**
   - В коллекции выберите запрос **"Get Users with Programs"**
   - Нажмите кнопку **Send**
   - Увидите ответ с данными пользователей

### Вариант 2: cURL (командная строка)

```bash
curl -H "X-API-Key: dotainstructor" http://localhost:8000/api/users
```

Для красивого вывода (если установлен `jq`):

```bash
curl -H "X-API-Key: dotainstructor" http://localhost:8000/api/users | jq
```

### Вариант 3: PowerShell (Windows)

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/users" -Headers @{"X-API-Key"="dotainstructor"}
```

### Вариант 4: Браузер (только для GET без авторизации)

⚠️ **Внимание:** Браузер не может отправить заголовок `X-API-Key`, поэтому получите ошибку 401.

Для тестирования без авторизации используйте:

```
http://localhost:8000/health
```

Или:

```
http://localhost:8000/
```

### Вариант 5: Python (requests)

```python
import requests

url = "http://localhost:8000/api/users"
headers = {"X-API-Key": "dotainstructor"}

response = requests.get(url, headers=headers)
print(response.json())
```

### Вариант 6: JavaScript (fetch)

```javascript
fetch('http://localhost:8000/api/users', {
  headers: {
    'X-API-Key': 'dotainstructor'
  }
})
  .then(response => response.json())
  .then(data => console.log(data));
```

## Проверка работы

### 1. Проверка доступности API

```bash
curl http://localhost:8000/health
```

Должен вернуть:
```json
{"status": "ok"}
```

### 2. Проверка корневого endpoint

```bash
curl http://localhost:8000/
```

Должен вернуть информацию об API.

### 3. Проверка основного endpoint

```bash
curl -H "X-API-Key: dotainstructor" http://localhost:8000/api/users
```

Должен вернуть JSON с пользователями и программами.

## Ожидаемый ответ

При успешном запросе вы получите:

```json
{
  "users": [
    {
      "id": 1,
      "telegram_id": 123456789,
      "username": "user123",
      "created_at": "2025-01-01T12:00:00",
      "programs_count": 2,
      "programs": [
        {
          "id": 1,
          "name": "Программа тренировок",
          "created_at": "2025-01-01T12:00:00"
        }
      ]
    }
  ],
  "total_users": 1,
  "total_programs": 2
}
```

## Возможные ошибки

### Ошибка: Connection refused

**Причина:** API сервер не запущен

**Решение:** Запустите `python api_server.py`

### Ошибка: 401 Unauthorized

**Причина:** Не указан заголовок `X-API-Key`

**Решение:** Добавьте заголовок `X-API-Key: dotainstructor`

### Ошибка: 403 Forbidden

**Причина:** Неверный API ключ

**Решение:** Проверьте, что используете `dotainstructor`

### Ошибка: ModuleNotFoundError

**Причина:** Не установлены зависимости

**Решение:** Выполните `pip install -r requirements.txt`

## Запуск на Railway

Если вы развернули API на Railway:

1. Получите URL вашего сервиса (например: `https://your-app.railway.app`)
2. Используйте этот URL вместо `localhost:8000`
3. Остальное остается тем же

Пример:
```bash
curl -H "X-API-Key: dotainstructor" https://your-app.railway.app/api/users
```

## Swagger UI (интерактивная документация)

После запуска сервера откройте в браузере:

```
http://localhost:8000/docs
```

Здесь можно:
- Увидеть все endpoints
- Протестировать API прямо в браузере
- Увидеть схемы данных

⚠️ **Важно:** В Swagger UI нужно будет ввести API ключ `dotainstructor` в поле авторизации.

## Быстрая проверка

Выполните эту команду для быстрой проверки:

```bash
# Проверка здоровья
curl http://localhost:8000/health

# Проверка основного endpoint
curl -H "X-API-Key: dotainstructor" http://localhost:8000/api/users
```

Если обе команды работают - API настроен правильно! ✅

