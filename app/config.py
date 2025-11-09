"""Конфигурация бота."""
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не установлен в переменных окружения")

# Путь к базе данных
# Для Railway: используем /data (монтируется как Volume для персистентности)
# Для локальной разработки: используем текущую директорию
# Railway устанавливает переменную RAILWAY_ENVIRONMENT
if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY"):
    # Railway - используем /data для персистентного хранилища
    DB_PATH = os.getenv("DATABASE_PATH", "/data/fitness_bot.db")
    # Создаём директорию, если её нет
    try:
        os.makedirs("/data", exist_ok=True)
    except Exception:
        pass  # Если директория уже существует или нет прав
else:
    # Локальная разработка
    DB_PATH = os.getenv("DATABASE_PATH", "fitness_bot.db")

DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

# Лимиты
MAX_PROGRAMS_PER_USER = 2

