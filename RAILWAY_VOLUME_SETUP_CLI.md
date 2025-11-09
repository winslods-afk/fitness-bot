# Быстрая настройка Volume через Railway CLI

## Если в Dashboard нет возможности создать volume

Используйте Railway CLI для создания и настройки volume.

## Шаги

### 1. Установите Railway CLI (если еще не установлен)

```bash
npm i -g @railway/cli
```

### 2. Войдите в Railway

```bash
railway login
```

Откроется браузер для авторизации.

### 3. Свяжите проект

```bash
cd C:\Users\Roman\fitness-bot
railway link
```

Выберите ваш проект из списка.

### 4. Выберите сервис

```bash
railway service
```

Или посмотрите список сервисов:
```bash
railway service list
```

Запомните имя сервиса (обычно это `web` или имя вашего сервиса).

### 5. Создайте volume

```bash
railway volume create database-storage
```

### 6. Привяжите volume к сервису

Замените `web` на имя вашего сервиса:

```bash
railway volume mount database-storage --service web --mount-path /data
```

Если ваш сервис называется по-другому, используйте его имя:
```bash
railway volume mount database-storage --service YOUR_SERVICE_NAME --mount-path /data
```

### 7. Проверьте, что volume создан

```bash
railway volume list
```

Должен появиться volume `database-storage`.

### 8. Деплой

Теперь сделайте коммит и пуш изменений:

```bash
git add -A
git commit -m "Configure persistent storage"
git push
```

Railway автоматически применит конфигурацию при следующем деплое.

## Проверка

После деплоя проверьте логи:

```bash
railway logs
```

Должно быть сообщение: `База данных инициализирована`

## Если что-то пошло не так

### Ошибка: "service not found"

Узнайте правильное имя сервиса:
```bash
railway service list
```

Используйте правильное имя в команде mount.

### Ошибка: "volume already exists"

Volume уже создан, просто привяжите его:
```bash
railway volume mount database-storage --service web --mount-path /data
```

### Ошибка: "mount path already in use"

Попробуйте использовать другой путь, например `/db`:
```bash
railway volume mount database-storage --service web --mount-path /db
```

И обновите `app/config.py`:
```python
DB_DIR = "/db"
```

## Альтернатива: Проверка через Dashboard

После создания volume через CLI, вы можете проверить его в Dashboard:
- Railway Dashboard → Ваш проект → Ваш сервис → Volumes
- Должен быть volume `database-storage` с mount path `/data`

