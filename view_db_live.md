# 📊 Просмотр базы данных в реальном времени (Railway)

Эта инструкция поможет вам настроить просмотр базы данных с Railway в реальном времени.

## 🚀 Быстрый старт

### Вариант 1: Автоматическая синхронизация (рекомендуется)

1. **Установите Railway CLI** (если еще не установлен):
   ```powershell
   npm i -g @railway/cli
   ```

2. **Войдите в Railway**:
   ```powershell
   railway login
   ```

3. **Подключите проект**:
   ```powershell
   cd C:\Users\Roman\fitness-bot
   railway link
   ```
   Выберите ваш проект из списка.

4. **Синхронизируйте базу данных**:
   ```powershell
   python sync_db.py
   ```
   
   Это создаст файл `fitness_bot_remote.db` в папке проекта.

5. **Откройте в DBeaver**:
   - Запустите DBeaver
   - Создайте новое подключение к SQLite
   - Укажите путь: `C:\Users\Roman\fitness-bot\fitness_bot_remote.db`

6. **Настройте автоматическое обновление**:
   
   **В DBeaver:**
   - Правой кнопкой на подключение → **Edit Connection**
   - Вкладка **Connection settings** → **Auto-commit** (включите)
   - Вкладка **SQL Editor** → **Auto-refresh** (включите, интервал 30 секунд)
   
   **Для обновления данных:**
   - Правой кнопкой на таблицу → **Refresh**
   - Или нажмите `F5`

   **Для автоматической синхронизации:**
   - Создайте задачу в Windows Task Scheduler
   - Или используйте PowerShell скрипт (см. ниже)

---

## 🔄 Автоматическое обновление базы данных

### Способ 1: PowerShell скрипт с циклом

Создайте файл `sync_db_loop.ps1`:

```powershell
# sync_db_loop.ps1
# Синхронизирует базу данных каждые 60 секунд

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$dbScript = Join-Path $scriptPath "sync_db.py"

Write-Host "🔄 Запуск автоматической синхронизации БД..."
Write-Host "Нажмите Ctrl+C для остановки"
Write-Host ""

while ($true) {
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Синхронизация..."
    python $dbScript
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Успешно обновлено" -ForegroundColor Green
    } else {
        Write-Host "❌ Ошибка при обновлении" -ForegroundColor Red
    }
    
    Write-Host "Ожидание 60 секунд до следующего обновления..."
    Write-Host ""
    Start-Sleep -Seconds 60
}
```

**Запуск:**
```powershell
cd C:\Users\Roman\fitness-bot
.\sync_db_loop.ps1
```

### Способ 2: Windows Task Scheduler

1. Откройте **Планировщик заданий** (Task Scheduler)
2. Создайте **Простую задачу**
3. Настройте:
   - **Триггер:** Каждые 5 минут
   - **Действие:** Запустить программу
   - **Программа:** `python`
   - **Аргументы:** `C:\Users\Roman\fitness-bot\sync_db.py`
   - **Рабочая папка:** `C:\Users\Roman\fitness-bot`

---

## 📱 Вариант 2: Через команду бота `/export_db`

Если вы настроили команду `/export_db` в боте:

1. **Добавьте свой Telegram ID в `app/handlers/start.py`**:
   ```python
   ADMIN_IDS = [ВАШ_TELEGRAM_ID]  # Например: [123456789]
   ```

2. **Отправьте команду в боте**:
   ```
   /export_db
   ```

3. **Сохраните файл** и откройте в DBeaver

**Недостаток:** Нужно вручную запрашивать обновление

---

## 🌐 Вариант 3: Веб-интерфейс (продвинутый)

Можно создать простой веб-интерфейс для просмотра БД. Создайте файл `web_viewer.py`:

```python
# web_viewer.py
from flask import Flask, render_template_string
from app.db.init_db import async_session_maker
from app.db.models import User, Session
from sqlalchemy import select
import asyncio

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Fitness Bot Database</title>
    <meta http-equiv="refresh" content="30">
    <style>
        body { font-family: Arial; margin: 20px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #4CAF50; color: white; }
    </style>
</head>
<body>
    <h1>📊 Fitness Bot Database</h1>
    <p>Обновляется каждые 30 секунд</p>
    
    <h2>Пользователи ({{ users_count }})</h2>
    <table>
        <tr>
            <th>ID</th>
            <th>Telegram ID</th>
            <th>Дата регистрации</th>
            <th>Программ</th>
        </tr>
        {% for user in users %}
        <tr>
            <td>{{ user.id }}</td>
            <td>{{ user.telegram_id }}</td>
            <td>{{ user.created_at }}</td>
            <td>{{ user.programs_count }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

async def get_users():
    async with async_session_maker() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        # Получаем количество программ для каждого пользователя
        for user in users:
            programs_result = await session.execute(
                select(Session).where(Session.user_id == user.id)
            )
            user.programs_count = len(programs_result.scalars().all())
        return users

@app.route('/')
def index():
    users = asyncio.run(get_users())
    return render_template_string(HTML_TEMPLATE, users=users, users_count=len(users))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

**Запуск:**
```powershell
python web_viewer.py
```

Откройте в браузере: `http://localhost:5000`

---

## 💡 Рекомендации

### Для ежедневного использования:

1. **Используйте скрипт синхронизации** (`sync_db.py`) для обновления БД
2. **Откройте БД в DBeaver** для удобного просмотра
3. **Настройте автоматическое обновление** через Task Scheduler или PowerShell скрипт

### Для быстрого просмотра:

1. Используйте команду `/export_db` в боте
2. Или запустите `sync_db.py` вручную

### Для мониторинга:

1. Создайте веб-интерфейс (см. Вариант 3)
2. Или используйте PowerShell скрипт с циклом

---

## 🔍 Полезные SQL запросы для DBeaver

### Просмотр всех пользователей:
```sql
SELECT * FROM users;
```

### Просмотр программ пользователя:
```sql
SELECT 
    u.telegram_id,
    s.name as program_name,
    s.created_at
FROM users u
JOIN sessions s ON u.id = s.user_id
ORDER BY s.created_at DESC;
```

### Статистика по программам:
```sql
SELECT 
    u.telegram_id,
    COUNT(s.session_id) as programs_count,
    COUNT(DISTINCT wd.id) as total_days,
    COUNT(DISTINCT e.exercise_id) as total_exercises
FROM users u
LEFT JOIN sessions s ON u.id = s.user_id
LEFT JOIN workout_days wd ON s.session_id = wd.session_id
LEFT JOIN exercises e ON wd.id = e.workout_day_id
GROUP BY u.id, u.telegram_id;
```

### Последние тренировки:
```sql
SELECT 
    u.telegram_id,
    s.name as program_name,
    sr.started_at,
    COUNT(DISTINCT ps.id) as sets_completed
FROM users u
JOIN sessions s ON u.id = s.user_id
JOIN session_runs sr ON s.session_id = sr.session_id
LEFT JOIN performed_sets ps ON sr.id = ps.session_run_id
GROUP BY sr.id
ORDER BY sr.started_at DESC
LIMIT 20;
```

---

## ⚠️ Важно

- **Не редактируйте базу данных напрямую** на продакшене
- **Делайте бэкапы** перед любыми изменениями
- **Используйте транзакции** для изменений
- **Проверяйте данные** перед применением изменений

---

## 🆘 Решение проблем

### Railway CLI не найден:
```powershell
npm i -g @railway/cli
```

### Проект не подключен:
```powershell
railway link
```

### База данных не найдена:
Проверьте путь к БД в `app/config.py`:
```python
DB_PATH = os.getenv("DATABASE_PATH", "fitness_bot.db")
```

На Railway база может быть в папке `data/`:
```powershell
railway run cat data/fitness_bot.db > fitness_bot_remote.db
```

---

**Готово!** Теперь вы можете просматривать базу данных в реальном времени. 🎉

