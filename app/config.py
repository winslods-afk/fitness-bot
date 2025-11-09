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
logger.info("=" * 60)
logger.info("DATABASE CONFIGURATION")
logger.info("=" * 60)
logger.info(f"Railway environment detected: {IS_RAILWAY}")
logger.info(f"Data volume exists: {HAS_DATA_VOLUME}")
logger.info(f"DATABASE_URL provided: {DATABASE_URL is not None}")

# Логируем все переменные Railway для отладки
if IS_RAILWAY:
    logger.info("Railway environment variables:")
    for var in RAILWAY_ENV_VARS:
        value = os.getenv(var)
        if value:
            logger.info(f"  {var} = {value}")
    
    # Проверяем директорию /data
    if os.path.exists("/data"):
        logger.info("Directory /data details:")
        logger.info(f"  Path: /data")
        logger.info(f"  Exists: {os.path.exists('/data')}")
        logger.info(f"  Is directory: {os.path.isdir('/data')}")
        logger.info(f"  Writable: {os.access('/data', os.W_OK)}")
        try:
            contents = os.listdir("/data")
            logger.info(f"  Contents: {contents}")
        except Exception as e:
            logger.error(f"  Error listing /data: {e}")
    else:
        logger.warning("Directory /data does not exist!")

# Инициализируем DB_PATH как None по умолчанию
DB_PATH = None

if not DATABASE_URL:
    # Fallback на SQLite для локальной разработки или если PostgreSQL не настроен
    if IS_RAILWAY:
        # Railway deployment - используем персистентное хранилище для SQLite
        DB_DIR = "/data"
        
        # Проверяем, существует ли директория /data (volume)
        volume_exists = os.path.exists(DB_DIR) and os.path.isdir(DB_DIR)
        volume_writable = os.access(DB_DIR, os.W_OK) if volume_exists else False
        
        logger.info(f"Volume /data check: exists={volume_exists}, writable={volume_writable}")
        
        if not volume_exists:
            logger.error(
                f"❌ Директория {DB_DIR} не существует!\n"
                f"⚠️ Volume не настроен! Данные БУДУТ теряться при деплое!\n"
                f"⚠️ Настройте volume: railway volume add --mount-path /data\n"
                f"⚠️ Или используйте PostgreSQL для автоматического сохранения данных"
            )
            # Пытаемся создать директорию (может не сработать, если volume не настроен)
            try:
                os.makedirs(DB_DIR, exist_ok=True)
                volume_exists = os.path.exists(DB_DIR)
                logger.info(f"Попытка создать директорию {DB_DIR}: success={volume_exists}")
            except Exception as e:
                logger.error(f"Не удалось создать директорию {DB_DIR}: {e}")
        
        if volume_exists and volume_writable:
            DB_PATH = os.path.join(DB_DIR, "fitness_bot.db")
            DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"
            logger.info(f"✅ Using SQLite on Railway: {DB_PATH}")
            logger.info("✅ Volume /data настроен правильно - данные будут сохраняться")
        else:
            # Volume не работает, используем fallback (данные будут теряться!)
            logger.error(
                f"❌ Volume /data недоступен! Данные БУДУТ теряться при деплое!\n"
                f"⚠️ Настройте volume: railway volume add --mount-path /data\n"
                f"⚠️ Или используйте PostgreSQL для автоматического сохранения данных\n"
                f"⚠️ Используется fallback путь (данные могут теряться!)"
            )
            # Fallback на текущую директорию (данные будут теряться при деплое!)
            DB_PATH = os.path.join(os.getcwd(), "fitness_bot.db")
            DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"
            logger.warning(f"⚠️ Fallback database path: {DB_PATH}")
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

