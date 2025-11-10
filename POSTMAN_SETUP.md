# Настройка Postman для тестирования API

## Быстрый старт

### 1. Запустите API сервер

```bash
python api_server.py
```

API будет доступен по адресу: `http://localhost:8000`

### 2. Настройка запроса в Postman

#### Создание нового запроса

1. Откройте Postman
2. Нажмите **"New"** → **"HTTP Request"**
3. Выберите метод: **GET**
4. Введите URL: `http://localhost:8000/api/users`

#### Настройка заголовков

1. Перейдите на вкладку **"Headers"**
2. Добавьте заголовок:
   - **Key:** `X-API-Key`
   - **Value:** `dotainstructor`

#### Отправка запроса

Нажмите кнопку **"Send"**

### 3. Ожидаемый ответ

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

## Импорт коллекции Postman

### Вариант 1: Импорт из файла

1. Откройте Postman
2. Нажмите **"Import"** (кнопка в левом верхнем углу)
3. Выберите файл `Fitness_Bot_API.postman_collection.json`
4. Коллекция будет добавлена в ваше рабочее пространство

### Вариант 2: Импорт из URL (если файл в репозитории)

1. Откройте Postman
2. Нажмите **"Import"**
3. Выберите вкладку **"Link"**
4. Вставьте URL к файлу коллекции

### Вариант 3: Ручное создание

Следуйте инструкциям выше в разделе "Быстрый старт"

## Настройка переменных окружения (опционально)

Для удобства можно создать переменные окружения:

1. В Postman нажмите на иконку **"Environments"** (слева)
2. Нажмите **"+"** для создания нового окружения
3. Добавьте переменные:
   - `base_url` = `http://localhost:8000`
   - `api_key` = `dotainstructor`
4. Сохраните окружение

Теперь в запросах можно использовать:
- URL: `{{base_url}}/api/users`
- Header: `X-API-Key: {{api_key}}`

## Тестирование на Railway

Если API развернут на Railway:

1. Получите URL вашего сервиса (например: `https://your-app.railway.app`)
2. В Postman используйте этот URL вместо `localhost:8000`
3. Остальные настройки остаются теми же

## Проверка ответов

### Успешный ответ (200 OK)

- Status: `200 OK`
- Body содержит JSON с данными пользователей

### Ошибка авторизации (401 Unauthorized)

Если не указан API ключ:
```json
{
  "detail": "API ключ отсутствует. Укажите заголовок X-API-Key"
}
```

### Ошибка доступа (403 Forbidden)

Если указан неверный API ключ:
```json
{
  "detail": "Неверный API ключ"
}
```

## Автоматические тесты в Postman

Можно добавить тесты для автоматической проверки:

1. Перейдите на вкладку **"Tests"** в запросе
2. Добавьте следующий код:

```javascript
// Проверка статуса ответа
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

// Проверка структуры ответа
pm.test("Response has users array", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('users');
    pm.expect(jsonData.users).to.be.an('array');
});

// Проверка наличия данных
pm.test("Response has total_users", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('total_users');
    pm.expect(jsonData.total_users).to.be.a('number');
});
```

## Troubleshooting

### CORS ошибки

Если возникают CORS ошибки:
- Убедитесь, что CORS настроен в `app/api/main.py`
- Проверьте, что сервер запущен и доступен

### Connection refused

- Убедитесь, что API сервер запущен
- Проверьте правильность URL и порта

### 401/403 ошибки

- Проверьте, что заголовок `X-API-Key` добавлен правильно
- Убедитесь, что значение API ключа: `dotainstructor`

