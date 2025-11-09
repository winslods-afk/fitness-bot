# Получение публичного DATABASE_URL для внешнего доступа

## Проблема

Если вы видите хост `postgres.railway.internal` в DATABASE_URL, это **внутренний хост**, который доступен только для сервисов внутри Railway. Для подключения извне (например, через DBeaver) нужен **публичный хост**.

## Решение

### Способ 1: Через Railway Dashboard (рекомендуется)

1. **Откройте Railway Dashboard:**
   - Перейдите на https://railway.app
   - Выберите ваш проект

2. **Откройте PostgreSQL сервис:**
   - Нажмите на сервис PostgreSQL (не на сервис бота)
   - Откройте вкладку **"Variables"** или **"Connect"**

3. **Найдите публичный DATABASE_URL:**
   - Ищите переменную `DATABASE_URL` или `PUBLIC_DATABASE_URL`
   - Или перейдите на вкладку **"Connect"** → **"Postgres Connection URL"**
   - Скопируйте URL, который начинается с `postgresql://` и содержит публичный хост (не `*.internal`)

4. **Публичный хост выглядит так:**
   ```
   postgresql://postgres:password@containers-us-west-xxx.railway.app:5432/railway
   ```
   или
   ```
   postgresql://postgres:password@xxx.up.railway.app:5432/railway
   ```

### Способ 2: Через Railway CLI

```bash
# Получите все переменные PostgreSQL сервиса
railway service  # Выберите PostgreSQL сервис
railway variables

# Или получите конкретную переменную
railway variables get DATABASE_URL
```

**Важно:** Убедитесь, что вы выбрали **PostgreSQL сервис**, а не сервис бота, так как у них разные переменные окружения.

### Способ 3: Через Railway CLI (выбор сервиса)

```bash
# Посмотрите список сервисов
railway service list

# Выберите PostgreSQL сервис
railway service  # Выберите PostgreSQL из списка

# Получите DATABASE_URL
railway variables get DATABASE_URL
```

### Способ 4: Получение через Railway Dashboard → Connect

1. **Откройте PostgreSQL сервис в Railway Dashboard**
2. **Перейдите на вкладку "Connect"** или **"Variables"**
3. **Найдите секцию "Postgres Connection URL"** или **"Connection URL"**
4. **Скопируйте публичный URL** (должен содержать публичный хост, не `*.internal`)

## Как отличить внутренний и публичный хост?

### Внутренний хост (не подходит для DBeaver):
```
postgresql://postgres:password@postgres.railway.internal:5432/railway
                                      ^^^^^^^^^^^^^^^^^^^^
                                      *.railway.internal
```

### Публичный хост (подходит для DBeaver):
```
postgresql://postgres:password@containers-us-west-xxx.railway.app:5432/railway
                                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                      *.railway.app или *.up.railway.app
```

## Если публичный хост недоступен

Если Railway не предоставляет публичный хост (на некоторых тарифах), используйте альтернативные методы:

### Альтернатива 1: Railway CLI подключение

```bash
# Подключение через Railway CLI
railway service  # Выберите PostgreSQL
railway connect postgres
```

Это откроет интерактивную сессию PostgreSQL в терминале.

### Альтернатива 2: SSH туннель (продвинутый)

Если у вас есть доступ к SSH, можно создать туннель, но это сложнее и обычно не требуется.

### Альтернатива 3: Использование Railway Proxy

Railway предоставляет прокси для доступа к базам данных, но это требует дополнительной настройки.

## Проверка подключения

После получения публичного DATABASE_URL:

1. **Парсинг DATABASE_URL:**
   ```
   postgresql://username:password@host:port/database
   ```

2. **Использование в DBeaver:**
   - Хост: часть после `@` и до `:`
   - Порт: часть после `:` и до `/`
   - База данных: часть после `/`
   - Пользователь: часть после `//` и до `:`
   - Пароль: часть после `:` и до `@`

3. **Настройка SSL:**
   - Обязательно включите SSL в DBeaver
   - Режим SSL: `require` или `prefer`

## Важные замечания

- ✅ **Публичный хост доступен извне** - можно подключаться через DBeaver
- ✅ **Внутренний хост доступен только внутри Railway** - не работает для внешних подключений
- ⚠️ **Безопасность** - публичный хост защищен SSL и паролем
- ⚠️ **Храните DATABASE_URL в секрете** - не публикуйте в открытом доступе

## Решение проблемы "Invalid JDBC URL"

Если вы получаете ошибку `Invalid JDBC URL: postgresql://...@postgres.railway.internal:5432/railway`:

1. **Проблема:** Используется внутренний хост `*.railway.internal`
2. **Решение:** Получите публичный DATABASE_URL через Railway Dashboard или CLI
3. **Проверка:** Убедитесь, что хост содержит `*.railway.app` или `*.up.railway.app`, а не `*.internal`

## Пример правильного DATABASE_URL

```
postgresql://postgres:password@containers-us-west-123.railway.app:5432/railway
```

Где:
- `postgres` - пользователь
- `password` - пароль
- `containers-us-west-123.railway.app` - **публичный хост** ✅
- `5432` - порт
- `railway` - база данных

## Дополнительная помощь

Если у вас все еще проблемы:

1. **Проверьте тариф Railway:**
   - Некоторые тарифы могут не предоставлять публичный доступ
   - Убедитесь, что у вас есть доступ к публичному хосту

2. **Обратитесь в поддержку Railway:**
   - https://railway.app/help
   - Или через Discord: https://discord.gg/railway

3. **Используйте Railway CLI:**
   - `railway connect postgres` - самый простой способ подключения

