"""Инициализация базы данных."""
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config import DATABASE_URL
from app.db.models import Base

logger = logging.getLogger(__name__)

# Создаём async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True
)

# Создаём session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_db():
    """Создание всех таблиц в базе данных."""
    from app.config import DB_PATH, DATABASE_URL, IS_RAILWAY, HAS_DATA_VOLUME
    import os
    
    logger.info("Инициализация базы данных...")
    
    # Определяем тип базы данных по DATABASE_URL
    is_postgresql = DATABASE_URL.startswith("postgresql+asyncpg://") or DATABASE_URL.startswith("postgresql://")
    is_sqlite = DATABASE_URL.startswith("sqlite+aiosqlite://") or DATABASE_URL.startswith("sqlite://")
    
    logger.info(f"Database type: {'PostgreSQL' if is_postgresql else 'SQLite' if is_sqlite else 'Unknown'}")
    logger.info(f"Database URL: {DATABASE_URL.split('@')[0] if '@' in DATABASE_URL else DATABASE_URL.split('://')[0] + '://***'}")
    
    if is_sqlite and DB_PATH:
        logger.info(f"SQLite database path: {DB_PATH}")
        
        # Проверяем, существует ли файл базы данных
        db_exists = os.path.exists(DB_PATH)
        logger.info(f"Database file exists: {db_exists}")
        
        # Проверяем директорию
        db_dir = os.path.dirname(DB_PATH)
        dir_exists = os.path.exists(db_dir)
        dir_writable = os.access(db_dir, os.W_OK) if dir_exists else False
        
        logger.info(f"Database directory: {db_dir}")
        logger.info(f"Directory exists: {dir_exists}")
        logger.info(f"Directory writable: {dir_writable}")
        
        if IS_RAILWAY:
            if HAS_DATA_VOLUME:
                logger.info("✅ Volume /data найден - данные будут сохраняться")
            else:
                logger.warning("⚠️ Volume /data НЕ найден - данные могут теряться при деплое!")
                logger.warning("⚠️ Настройте volume: railway volume add --mount-path /data")
            
            # Дополнительная проверка для Railway
            if db_dir == "/data":
                if dir_exists and dir_writable:
                    logger.info("✅ Директория /data доступна для записи")
                else:
                    logger.error(f"❌ Директория /data недоступна! exists={dir_exists}, writable={dir_writable}")
        else:
            logger.info("Локальная разработка - SQLite")
    elif is_postgresql:
        logger.info("PostgreSQL database - данные сохраняются автоматически")
    else:
        logger.warning(f"Неизвестный тип базы данных: {DATABASE_URL[:50]}...")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Проверяем, создался ли файл базы данных (для SQLite)
    if is_sqlite and DB_PATH:
        db_exists_after = os.path.exists(DB_PATH)
        if db_exists_after:
            db_size = os.path.getsize(DB_PATH) if db_exists_after else 0
            logger.info(f"✅ База данных создана: {DB_PATH} (размер: {db_size} байт)")
        else:
            logger.warning(f"⚠️ Файл базы данных не найден после создания: {DB_PATH}")
    
    logger.info("✅ База данных инициализирована")


async def close_db():
    """Закрытие соединения с базой данных."""
    await engine.dispose()
    logger.info("Соединение с базой данных закрыто")


async def get_session() -> AsyncSession:
    """Получить сессию базы данных."""
    async with async_session_maker() as session:
        yield session

