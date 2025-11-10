# API CRUD Документация

Полная документация по работе с базой данных через API.

## Аутентификация

Все endpoints требуют API ключ в заголовке:
```
X-API-Key: dotainstructor
```

## Endpoints

### Пользователи (Users)

#### GET /api/users
Получить список всех пользователей с их программами.

**Ответ:**
```json
{
  "users": [
    {
      "id": 1,
      "telegram_id": 123456789,
      "username": "user123",
      "created_at": "2024-01-01T00:00:00",
      "programs_count": 2,
      "programs": [...]
    }
  ],
  "total_users": 1,
  "total_programs": 2
}
```

#### GET /api/users/{user_id}
Получить пользователя по ID.

**Ответ:**
```json
{
  "id": 1,
  "telegram_id": 123456789,
  "username": "user123",
  "created_at": "2024-01-01T00:00:00"
}
```

#### POST /api/users
Создать нового пользователя.

**Тело запроса:**
```json
{
  "telegram_id": 123456789,
  "username": "user123"
}
```

**Ответ:** 201 Created
```json
{
  "id": 1,
  "telegram_id": 123456789,
  "username": "user123",
  "created_at": "2024-01-01T00:00:00"
}
```

#### DELETE /api/users/{user_id}
Удалить пользователя и все связанные данные.

**Ответ:** 204 No Content

---

### Программы (Programs / Sessions)

#### GET /api/programs
Получить список всех программ.

**Query параметры:**
- `user_id` (опционально) - фильтр по пользователю

**Пример:** `/api/programs?user_id=1`

**Ответ:**
```json
[
  {
    "session_id": 1,
    "user_id": 1,
    "name": "Программа 1",
    "created_at": "2024-01-01T00:00:00"
  }
]
```

#### GET /api/programs/{program_id}
Получить программу с детальной информацией (дни, упражнения, подходы).

**Ответ:**
```json
{
  "session_id": 1,
  "user_id": 1,
  "name": "Программа 1",
  "created_at": "2024-01-01T00:00:00",
  "days": [
    {
      "id": 1,
      "session_id": 1,
      "name": "День 1: Грудь",
      "day_index": 0,
      "exercises": [
        {
          "exercise_id": 1,
          "workout_day_id": 1,
          "name": "Жим лежа",
          "order": 0,
          "sets": [
            {
              "set_id": 1,
              "exercise_id": 1,
              "set_index": 0,
              "reps": 10,
              "weight": 80.0
            }
          ]
        }
      ]
    }
  ]
}
```

#### POST /api/programs
Создать новую программу.

**Тело запроса:**
```json
{
  "user_id": 1,
  "name": "Новая программа"
}
```

**Ответ:** 201 Created
```json
{
  "session_id": 1,
  "user_id": 1,
  "name": "Новая программа",
  "created_at": "2024-01-01T00:00:00"
}
```

#### PUT /api/programs/{program_id}
Обновить программу.

**Тело запроса:**
```json
{
  "name": "Обновленное название"
}
```

**Ответ:**
```json
{
  "session_id": 1,
  "user_id": 1,
  "name": "Обновленное название",
  "created_at": "2024-01-01T00:00:00"
}
```

#### DELETE /api/programs/{program_id}
Удалить программу и все связанные данные.

**Ответ:** 204 No Content

---

### Дни тренировок (WorkoutDays)

#### GET /api/programs/{program_id}/days
Получить все дни программы.

**Ответ:**
```json
[
  {
    "id": 1,
    "session_id": 1,
    "name": "День 1: Грудь",
    "day_index": 0,
    "exercises": [...]
  }
]
```

#### POST /api/programs/{program_id}/days
Создать новый день в программе.

**Тело запроса:**
```json
{
  "session_id": 1,
  "name": "День 1: Грудь",
  "day_index": 0
}
```

**Примечание:** `session_id` должен совпадать с `program_id` в URL.

**Ответ:** 201 Created
```json
{
  "id": 1,
  "session_id": 1,
  "name": "День 1: Грудь",
  "day_index": 0,
  "exercises": []
}
```

---

### Упражнения (Exercises)

#### GET /api/exercises/{exercise_id}
Получить упражнение по ID.

**Ответ:**
```json
{
  "exercise_id": 1,
  "workout_day_id": 1,
  "name": "Жим лежа",
  "order": 0,
  "sets": [...]
}
```

#### POST /api/days/{day_id}/exercises
Создать новое упражнение в дне.

**Тело запроса:**
```json
{
  "workout_day_id": 1,
  "name": "Жим лежа",
  "order": 0
}
```

**Примечание:** `workout_day_id` должен совпадать с `day_id` в URL.

**Ответ:** 201 Created
```json
{
  "exercise_id": 1,
  "workout_day_id": 1,
  "name": "Жим лежа",
  "order": 0,
  "sets": []
}
```

#### PUT /api/exercises/{exercise_id}
Обновить упражнение.

**Тело запроса:**
```json
{
  "name": "Жим лежа на наклонной",
  "order": 1
}
```

**Ответ:**
```json
{
  "exercise_id": 1,
  "workout_day_id": 1,
  "name": "Жим лежа на наклонной",
  "order": 1,
  "sets": []
}
```

---

### Подходы (Sets)

#### POST /api/exercises/{exercise_id}/sets
Создать новый подход для упражнения.

**Тело запроса:**
```json
{
  "exercise_id": 1,
  "set_index": 0,
  "reps": 10,
  "weight": 80.0
}
```

**Примечание:** `exercise_id` должен совпадать с `exercise_id` в URL.

**Ответ:** 201 Created
```json
{
  "set_id": 1,
  "exercise_id": 1,
  "set_index": 0,
  "reps": 10,
  "weight": 80.0
}
```

---

### Запуски тренировок (SessionRuns)

#### GET /api/session-runs/{run_id}
Получить запуск тренировки по ID.

**Ответ:**
```json
{
  "id": 1,
  "user_id": 1,
  "session_id": 1,
  "started_at": "2024-01-01T00:00:00"
}
```

#### POST /api/session-runs
Создать новый запуск тренировки.

**Тело запроса:**
```json
{
  "user_id": 1,
  "session_id": 1
}
```

**Ответ:** 201 Created
```json
{
  "id": 1,
  "user_id": 1,
  "session_id": 1,
  "started_at": "2024-01-01T00:00:00"
}
```

---

### Выполненные подходы (PerformedSets)

#### POST /api/performed-sets
Создать запись о выполненном подходе.

**Тело запроса:**
```json
{
  "exercise_id": 1,
  "set_index": 0,
  "weight": 80.0,
  "session_run_id": 1
}
```

**Ответ:** 201 Created
```json
{
  "id": 1,
  "exercise_id": 1,
  "set_index": 0,
  "weight": 80.0,
  "session_run_id": 1,
  "timestamp": "2024-01-01T00:00:00"
}
```

#### GET /api/session-runs/{run_id}/performed-sets
Получить все выполненные подходы для запуска тренировки.

**Ответ:**
```json
[
  {
    "id": 1,
    "exercise_id": 1,
    "set_index": 0,
    "weight": 80.0,
    "session_run_id": 1,
    "timestamp": "2024-01-01T00:00:00"
  }
]
```

---

## Примеры использования

### Создание полной программы через API

1. **Создать пользователя:**
```bash
curl -X POST "https://your-api.railway.app/api/users" \
  -H "X-API-Key: dotainstructor" \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_id": 123456789,
    "username": "user123"
  }'
```

2. **Создать программу:**
```bash
curl -X POST "https://your-api.railway.app/api/programs" \
  -H "X-API-Key: dotainstructor" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "name": "Программа тренировок"
  }'
```

3. **Добавить день:**
```bash
curl -X POST "https://your-api.railway.app/api/programs/1/days" \
  -H "X-API-Key: dotainstructor" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": 1,
    "name": "День 1: Грудь",
    "day_index": 0
  }'
```

4. **Добавить упражнение:**
```bash
curl -X POST "https://your-api.railway.app/api/days/1/exercises" \
  -H "X-API-Key: dotainstructor" \
  -H "Content-Type: application/json" \
  -d '{
    "workout_day_id": 1,
    "name": "Жим лежа",
    "order": 0
  }'
```

5. **Добавить подход:**
```bash
curl -X POST "https://your-api.railway.app/api/exercises/1/sets" \
  -H "X-API-Key: dotainstructor" \
  -H "Content-Type: application/json" \
  -d '{
    "exercise_id": 1,
    "set_index": 0,
    "reps": 10,
    "weight": 80.0
  }'
```

### Получение данных

```bash
# Получить все программы пользователя
curl "https://your-api.railway.app/api/programs?user_id=1" \
  -H "X-API-Key: dotainstructor"

# Получить программу с деталями
curl "https://your-api.railway.app/api/programs/1" \
  -H "X-API-Key: dotainstructor"
```

## Коды ошибок

- `200 OK` - Успешный запрос
- `201 Created` - Ресурс создан
- `204 No Content` - Ресурс удален
- `400 Bad Request` - Неверный запрос
- `401 Unauthorized` - API ключ отсутствует
- `403 Forbidden` - Неверный API ключ
- `404 Not Found` - Ресурс не найден
- `500 Internal Server Error` - Ошибка сервера

## Swagger UI

Интерактивная документация доступна по адресу:
```
https://your-api.railway.app/docs
```

Там вы можете:
- Просмотреть все endpoints
- Протестировать запросы
- Увидеть схемы данных
- Проверить примеры ответов

