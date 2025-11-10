# Настройка API на Railway

## Проблема: Ошибка 502

Если вы получаете ошибку 502, это означает, что:
- Либо приложение не запускается
- Либо запущен бот вместо API сервера

## Решение: Настройка Procfile для API

### Вариант 1: Заменить Procfile (если нужен только API)

1. Откройте файл `Procfile`
2. Замените содержимое на:
   ```
   web: python api_server.py
   ```
3. Закоммитьте и запушьте:
   ```bash
   git add Procfile
   git commit -m "Configure Procfile for API server"
   git push
   ```
4. Railway автоматически перезапустит сервис

### Вариант 2: Создать отдельный сервис для API (рекомендуется)

1. В Railway Dashboard:
   - Нажмите **"+ New"** → **"GitHub Repo"**
   - Выберите ваш репозиторий
   - Создайте новый сервис

2. В новом сервисе:
   - Переименуйте `Procfile` в `Procfile.bot` (для бота)
   - Создайте новый `Procfile` с содержимым:
     ```
     web: python api_server.py
     ```

3. Настройте переменные окружения:
   - `DATABASE_URL` (должен быть установлен автоматически, если PostgreSQL подключен)
   - При необходимости добавьте другие переменные

4. Деплойте

### Вариант 3: Два сервиса (бот + API)

**Сервис 1 - Бот:**
- `Procfile`: `web: python -m app.main`
- Переменные: `TELEGRAM_BOT_TOKEN`, `DATABASE_URL`

**Сервис 2 - API:**
- `Procfile`: `web: python api_server.py`
- Переменные: `DATABASE_URL`

## Проверка после настройки

1. **Проверьте логи Railway:**
   - Должны увидеть: `INFO: Uvicorn running on http://0.0.0.0:XXXX`

2. **Проверьте health endpoint:**
   ```bash
   curl https://your-app.railway.app/health
   ```
   Должен вернуть: `{"status": "ok"}`

3. **Проверьте основной endpoint:**
   ```bash
   curl -H "X-API-Key: dotainstructor" https://your-app.railway.app/api/users
   ```

## Текущая ситуация

Сейчас в `Procfile` указано:
```
web: python -m app.main
```

Это запускает **бота**, а не API сервер. Поэтому API endpoint недоступен.

## Быстрое исправление

1. Измените `Procfile`:
   ```bash
   echo "web: python api_server.py" > Procfile
   ```

2. Закоммитьте:
   ```bash
   git add Procfile
   git commit -m "Switch to API server"
   git push
   ```

3. Railway автоматически перезапустит сервис

4. Проверьте через несколько минут:
   ```bash
   curl https://your-app.railway.app/health
   ```

## Если нужны и бот, и API

Создайте два отдельных сервиса в Railway - это рекомендуемый подход.

