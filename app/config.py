"""Конфигурация бота."""
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не установлен в переменных окружения")

# База данных
# Railway автоматически предоставляет DATABASE_URL для PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")

# Инициализируем DB_PATH как None по умолчанию
DB_PATH = None

if not DATABASE_URL:
    # Fallback на SQLite для локальной разработки или если PostgreSQL не настроен
    if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY"):
        # Railway deployment - используем персистентное хранилище для SQLite
        DB_DIR = "/data"
        os.makedirs(DB_DIR, exist_ok=True)
        DB_PATH = os.path.join(DB_DIR, "fitness_bot.db")
        DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"
    else:
        # Локальная разработка
        DB_PATH = os.getenv("DATABASE_PATH", "fitness_bot.db")
        DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"
else:
    # Если DATABASE_URL предоставлен (PostgreSQL), используем его
    # Преобразуем postgres:// в postgresql+asyncpg:// для SQLAlchemy async
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
    elif DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    # Для PostgreSQL DB_PATH остается None, так как это не файловая БД

# Лимиты
MAX_PROGRAMS_PER_USER = 2

