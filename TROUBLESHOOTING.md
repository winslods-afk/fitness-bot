# Устранение проблем с API

## Ошибка 502 "Application failed to respond"

### Причины:
1. Приложение не запускается
2. Приложение падает при инициализации
3. Неправильная конфигурация в Procfile
4. Проблемы с базой данных

### Решение:

#### 1. Проверьте Procfile
Должно быть:
```
web: python api_server.py
```

#### 2. Проверьте логи Railway
1. Откройте Railway Dashboard
2. Выберите ваш сервис
3. Перейдите в **Deployments** → последний деплой → **Logs**

Ищите ошибки:
- `ModuleNotFoundError` - не установлены зависимости
- `ImportError` - проблемы с импортами
- `Database connection error` - проблемы с БД
- `DATABASE_URL is None` - не установлена переменная окружения

#### 3. Проверьте переменные окружения
В Railway Dashboard → Ваш сервис → **Variables**:

**Обязательные:**
- `DATABASE_URL` - должен быть установлен (Railway устанавливает автоматически для PostgreSQL)

**Проверка формата:**
```
postgresql+asyncpg://user:password@host:port/database
```

#### 4. Проверьте зависимости
Убедитесь, что `requirements.txt` содержит:
```
fastapi==0.115.0
uvicorn[standard]==0.32.0
pydantic>=2.0.0
sqlalchemy[asyncio]==2.0.36
asyncpg==0.29.0
```

#### 5. Локальное тестирование
Перед деплоем протестируйте локально:

```bash
# Установите зависимости
pip install -r requirements.txt

# Установите DATABASE_URL
export DATABASE_URL="postgresql+asyncpg://..."

# Запустите сервер
python api_server.py
```

Если локально работает, но на Railway нет - проверьте переменные окружения.

### Типичные ошибки в логах:

#### "DATABASE_URL is None"
**Решение:** Убедитесь, что PostgreSQL сервис подключен к вашему сервису API в Railway.

#### "ModuleNotFoundError: No module named 'app'"
**Решение:** Убедитесь, что структура проекта правильная и все файлы закоммичены.

#### "Connection refused" или "Connection timeout"
**Решение:** Проверьте, что PostgreSQL сервис запущен и доступен.

#### "Port already in use"
**Решение:** Railway автоматически устанавливает PORT. Не указывайте порт вручную.

## Проверка работоспособности

После деплоя проверьте:

1. **Health endpoint:**
   ```bash
   curl https://your-app.railway.app/health
   ```
   Должен вернуть: `{"status": "ok"}`

2. **Корневой endpoint:**
   ```bash
   curl https://your-app.railway.app/
   ```
   Должен вернуть информацию об API.

3. **API endpoint:**
   ```bash
   curl -H "X-API-Key: dotainstructor" https://your-app.railway.app/api/users
   ```
   Должен вернуть список пользователей.

## Если ничего не помогает

1. Проверьте логи Railway полностью - там должна быть информация об ошибке
2. Убедитесь, что все файлы закоммичены и запушены
3. Попробуйте пересоздать сервис в Railway
4. Проверьте, что PostgreSQL сервис работает и доступен

