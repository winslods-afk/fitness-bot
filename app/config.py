"""Конфигурация бота."""
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не установлен в переменных окружения")

# Путь к базе данных
# Для Railway: используем /data (смонтированный volume)
# Для локальной разработки: используем текущую директорию
if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY"):
    # Railway deployment - используем персистентное хранилище
    DB_DIR = "/data"
    os.makedirs(DB_DIR, exist_ok=True)
    DB_PATH = os.path.join(DB_DIR, "fitness_bot.db")
else:
    # Локальная разработка
    DB_PATH = os.getenv("DATABASE_PATH", "fitness_bot.db")

DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

# Лимиты
MAX_PROGRAMS_PER_USER = 2

