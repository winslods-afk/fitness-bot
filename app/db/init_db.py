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
    logger.info(f"DATABASE_URL (raw): {DATABASE_URL}")
    logger.info(f"DB_PATH: {DB_PATH}")
    
    # Определяем тип базы данных по DATABASE_URL
    # Проверяем строку напрямую, не преобразуя в lower() сразу
    url_lower = DATABASE_URL.lower()
    is_postgresql = "postgresql" in url_lower or "postgres" in url_lower
    is_sqlite = "sqlite" in url_lower
    
    # Полный URL для логирования (без пароля)
    if "@" in DATABASE_URL:
        # PostgreSQL или другой URL с паролем
        url_parts = DATABASE_URL.split("@")
        safe_url = url_parts[0].split("://")[0] + "://***@" + "@".join(url_parts[1:])
    else:
        # SQLite - показываем полный путь
        safe_url = DATABASE_URL
    
    db_type = "PostgreSQL" if is_postgresql else ("SQLite" if is_sqlite else "Unknown")
    logger.info(f"Database type: {db_type}")
    logger.info(f"Database URL: {safe_url}")
    
    # Дополнительная проверка для SQLite
    if not is_sqlite and not is_postgresql:
        logger.error(f"❌ Не удалось определить тип базы данных из URL: {DATABASE_URL[:100]}")
        # Пытаемся определить по наличию DB_PATH
        if DB_PATH:
            logger.info("DB_PATH указан, предполагаем SQLite")
            is_sqlite = True
            db_type = "SQLite"
    
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
    
    # Создаем таблицы (только если их нет - create_all не перезаписывает существующие таблицы)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Таблицы проверены/созданы (существующие таблицы не перезаписываются)")
    
    # Проверяем, создался ли файл базы данных (для SQLite)
    if is_sqlite and DB_PATH:
        db_exists_after = os.path.exists(DB_PATH)
        if db_exists_after:
            try:
                db_size = os.path.getsize(DB_PATH)
                logger.info(f"✅ База данных: {DB_PATH} (размер: {db_size} байт)")
                
                # Дополнительная проверка для Railway - убеждаемся, что файл в volume
                if IS_RAILWAY:
                    db_dir = os.path.dirname(DB_PATH)
                    if db_dir == "/data":
                        logger.info("✅ База данных находится в volume /data - данные сохраняются")
                        # Проверяем содержимое директории /data
                        try:
                            data_contents = os.listdir("/data")
                            logger.info(f"Содержимое /data: {data_contents}")
                        except Exception as e:
                            logger.error(f"Ошибка при чтении /data: {e}")
                    else:
                        logger.error(f"❌ База данных НЕ в volume! Путь: {DB_PATH}")
                        logger.error("⚠️ Данные БУДУТ теряться при деплое!")
            except Exception as e:
                logger.error(f"Ошибка при проверке размера базы данных: {e}")
        else:
            logger.warning(f"⚠️ Файл базы данных не найден после создания: {DB_PATH}")
            logger.warning("⚠️ Это нормально при первом запуске, но файл должен появиться после первого использования")
    
    logger.info("✅ База данных инициализирована")


async def close_db():
    """Закрытие соединения с базой данных."""
    await engine.dispose()
    logger.info("Соединение с базой данных закрыто")


async def get_session() -> AsyncSession:
    """Получить сессию базы данных."""
    async with async_session_maker() as session:
        yield session

