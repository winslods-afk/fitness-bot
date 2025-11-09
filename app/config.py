"""Конфигурация бота."""
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не установлен в переменных окружения")

# Определение окружения Railway
# Railway устанавливает различные переменные окружения
RAILWAY_ENV_VARS = [
    "RAILWAY_ENVIRONMENT",
    "RAILWAY",
    "RAILWAY_SERVICE_NAME",
    "RAILWAY_PROJECT_ID",
    "RAILWAY_SERVICE_ID"
]
IS_RAILWAY = any(os.getenv(var) for var in RAILWAY_ENV_VARS)

# Проверка наличия директории /data (volume для SQLite)
HAS_DATA_VOLUME = os.path.exists("/data") and os.path.isdir("/data")

# База данных
# Railway автоматически предоставляет DATABASE_URL для PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")

# Логирование конфигурации
logger.info(f"Railway environment detected: {IS_RAILWAY}")
logger.info(f"Data volume exists: {HAS_DATA_VOLUME}")
logger.info(f"DATABASE_URL provided: {DATABASE_URL is not None}")

# Инициализируем DB_PATH как None по умолчанию
DB_PATH = None

if not DATABASE_URL:
    # Fallback на SQLite для локальной разработки или если PostgreSQL не настроен
    if IS_RAILWAY:
        # Railway deployment - используем персистентное хранилище для SQLite
        DB_DIR = "/data"
        try:
            os.makedirs(DB_DIR, exist_ok=True)
            DB_PATH = os.path.join(DB_DIR, "fitness_bot.db")
            DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"
            logger.info(f"Using SQLite on Railway: {DB_PATH}")
            
            # Проверяем, существует ли volume
            if not HAS_DATA_VOLUME:
                logger.warning(
                    "⚠️ Volume /data не найден! Данные могут теряться при деплое. "
                    "Настройте volume через Railway CLI: railway volume add --mount-path /data"
                )
        except Exception as e:
            logger.error(f"Ошибка при создании директории /data: {e}")
            # Fallback на текущую директорию (данные могут теряться)
            DB_PATH = "fitness_bot.db"
            DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"
            logger.warning(f"Используется fallback путь: {DB_PATH}")
    else:
        # Локальная разработка
        DB_PATH = os.getenv("DATABASE_PATH", "fitness_bot.db")
        DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"
        logger.info(f"Using SQLite locally: {DB_PATH}")
else:
    # Если DATABASE_URL предоставлен (PostgreSQL), используем его
    # Преобразуем postgres:// в postgresql+asyncpg:// для SQLAlchemy async
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
    elif DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    # Для PostgreSQL DB_PATH остается None, так как это не файловая БД
    logger.info("Using PostgreSQL database")
    logger.info(f"PostgreSQL connection URL: {DATABASE_URL.split('@')[0]}@***")  # Не логируем пароль

logger.info(f"Final DATABASE_URL: {DATABASE_URL.split('@')[0] if '@' in DATABASE_URL else DATABASE_URL}@***")
logger.info(f"Final DB_PATH: {DB_PATH}")

# Экспорт переменных для использования в других модулях
__all__ = [
    "BOT_TOKEN",
    "DATABASE_URL",
    "DB_PATH",
    "IS_RAILWAY",
    "HAS_DATA_VOLUME",
    "MAX_PROGRAMS_PER_USER"
]

# Лимиты
MAX_PROGRAMS_PER_USER = 2

