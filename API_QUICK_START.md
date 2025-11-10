# API Quick Start

## Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Запуск API сервера

```bash
python api_server.py
```

API будет доступен по адресу: `http://localhost:8000`

### 3. Тестирование API

#### Получить всех пользователей с программами:

```bash
curl -H "X-API-Key: dotainstructor" http://localhost:8000/api/users
```

#### Или через браузер (с расширением для заголовков):

Откройте: `http://localhost:8000/api/users`

Добавьте заголовок: `X-API-Key: dotainstructor`

### 4. Swagger UI (интерактивная документация)

Откройте в браузере: `http://localhost:8000/docs`

Здесь можно:
- Просмотреть все endpoints
- Протестировать API прямо в браузере
- Увидеть схемы данных

## Пример ответа

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

## На Railway

Для запуска API на Railway:

1. Добавьте в `Procfile` или настройте команду запуска:
   ```
   web: python api_server.py
   ```

2. Или интегрируйте с основным ботом (см. `API_DOCUMENTATION.md`)

3. Убедитесь, что порт настроен правильно (Railway автоматически устанавливает `PORT`)

## Безопасность

⚠️ **Важно:** API ключ `dotainstructor` хранится в коде. Для production рекомендуется вынести его в переменные окружения.

## Подробная документация

См. `API_DOCUMENTATION.md` для полной документации и примеров использования.

