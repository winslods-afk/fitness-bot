# API Документация

## Обзор

API предоставляет доступ к данным о пользователях и их программах тренировок через REST endpoints.

## Авторизация

Все API endpoints требуют авторизации через API ключ в заголовке `X-API-Key`.

**API Key:** `dotainstructor`

### Пример использования

```bash
curl -H "X-API-Key: dotainstructor" http://localhost:8000/api/users
```

## Endpoints

### GET /api/users

Получить список всех пользователей с их программами и количеством программ.

**Заголовки:**
- `X-API-Key: dotainstructor` (обязательно)

**Ответ:**

```json
{
  "users": [
    {
      "id": 1,
      "telegram_id": 123456789,
      "username": "username_here",
      "created_at": "2025-01-01T12:00:00",
      "programs_count": 2,
      "programs": [
        {
          "id": 1,
          "name": "Программа тренировок",
          "created_at": "2025-01-01T12:00:00"
        },
        {
          "id": 2,
          "name": "Другая программа",
          "created_at": "2025-01-02T12:00:00"
        }
      ]
    }
  ],
  "total_users": 1,
  "total_programs": 2
}
```

**Коды ответов:**
- `200 OK` - успешный запрос
- `401 Unauthorized` - отсутствует API ключ
- `403 Forbidden` - неверный API ключ
- `500 Internal Server Error` - ошибка сервера

## Запуск API сервера

### Локально

```bash
python api_server.py
```

API будет доступен по адресу: `http://localhost:8000`

### На Railway

1. Добавьте переменную окружения `API_PORT=8000` (опционально)
2. Запустите API сервер через `api_server.py` или интегрируйте с основным приложением

### Интеграция с ботом

API можно запускать параллельно с ботом, используя отдельный процесс или интегрировав в `main.py`.

## Swagger UI

После запуска API сервера доступна интерактивная документация:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Тестирование в Postman

### Быстрый импорт коллекции

1. Откройте Postman
2. Нажмите **"Import"** (кнопка в левом верхнем углу)
3. Выберите файл `Fitness_Bot_API.postman_collection.json`
4. Импортируйте окружение `Fitness_Bot_API.postman_environment.json` (опционально)

### Ручная настройка

1. Создайте новый запрос: **GET** `http://localhost:8000/api/users`
2. Добавьте заголовок: **X-API-Key** = `dotainstructor`
3. Отправьте запрос

Подробная инструкция: см. `POSTMAN_SETUP.md`

## Примеры использования

### Python (requests)

```python
import requests

url = "http://localhost:8000/api/users"
headers = {"X-API-Key": "dotainstructor"}

response = requests.get(url, headers=headers)
data = response.json()

print(f"Всего пользователей: {data['total_users']}")
print(f"Всего программ: {data['total_programs']}")

for user in data['users']:
    print(f"Пользователь: {user['username']} (ID: {user['telegram_id']})")
    print(f"  Программ: {user['programs_count']}")
    for program in user['programs']:
        print(f"    - {program['name']}")
```

### cURL

```bash
# Получить всех пользователей
curl -H "X-API-Key: dotainstructor" \
     http://localhost:8000/api/users

# С форматированием JSON
curl -H "X-API-Key: dotainstructor" \
     http://localhost:8000/api/users | jq
```

### JavaScript (fetch)

```javascript
fetch('http://localhost:8000/api/users', {
  headers: {
    'X-API-Key': 'dotainstructor'
  }
})
  .then(response => response.json())
  .then(data => {
    console.log('Всего пользователей:', data.total_users);
    console.log('Всего программ:', data.total_programs);
    data.users.forEach(user => {
      console.log(`Пользователь: ${user.username} (${user.programs_count} программ)`);
    });
  });
```

## Безопасность

⚠️ **Важно:** API ключ хранится в коде. Для production рекомендуется:

1. Вынести API ключ в переменные окружения
2. Использовать более сложную систему авторизации (JWT, OAuth)
3. Ограничить доступ по IP адресам
4. Использовать HTTPS

## Ошибки

### 401 Unauthorized

```json
{
  "detail": "API ключ отсутствует. Укажите заголовок X-API-Key"
}
```

**Решение:** Добавьте заголовок `X-API-Key` в запрос.

### 403 Forbidden

```json
{
  "detail": "Неверный API ключ"
}
```

**Решение:** Проверьте правильность API ключа.

### 500 Internal Server Error

```json
{
  "detail": "Ошибка при получении данных: ..."
}
```

**Решение:** Проверьте логи сервера и состояние базы данных.

