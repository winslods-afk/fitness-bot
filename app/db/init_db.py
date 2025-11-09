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
    
    logger.info("Инициализация базы данных...")
    logger.info(f"Database URL: {DATABASE_URL.split('@')[0] if '@' in DATABASE_URL else DATABASE_URL}@***")
    
    if DB_PATH:
        logger.info(f"SQLite database path: {DB_PATH}")
        if IS_RAILWAY:
            if HAS_DATA_VOLUME:
                logger.info("✅ Volume /data найден - данные будут сохраняться")
            else:
                logger.warning("⚠️ Volume /data НЕ найден - данные могут теряться при деплое!")
                logger.warning("⚠️ Настройте volume: railway volume add --mount-path /data")
    else:
        logger.info("PostgreSQL database - данные сохраняются автоматически")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ База данных инициализирована")


async def close_db():
    """Закрытие соединения с базой данных."""
    await engine.dispose()
    logger.info("Соединение с базой данных закрыто")


async def get_session() -> AsyncSession:
    """Получить сессию базы данных."""
    async with async_session_maker() as session:
        yield session

