"""Конфигурация бота."""
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не установлен в переменных окружения")

# Путь к базе данных (для хостинга используем /tmp или рабочую директорию)
DB_PATH = os.getenv("DATABASE_PATH", "fitness_bot.db")
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

# Лимиты
MAX_PROGRAMS_PER_USER = 2

