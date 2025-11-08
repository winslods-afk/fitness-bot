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
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("База данных инициализирована")


async def close_db():
    """Закрытие соединения с базой данных."""
    await engine.dispose()
    logger.info("Соединение с базой данных закрыто")


async def get_session() -> AsyncSession:
    """Получить сессию базы данных."""
    async with async_session_maker() as session:
        yield session

