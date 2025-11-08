FROM python:3.11-slim

WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY app/ ./app/

# Создаём директорию для базы данных
RUN mkdir -p /app/data

# Устанавливаем переменную окружения для базы данных
ENV DATABASE_URL=sqlite+aiosqlite:///data/fitness_bot.db

# Запускаем бота
CMD ["python", "-m", "app.main"]

