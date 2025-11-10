"""FastAPI приложение для API endpoints."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan контекст для инициализации и очистки."""
    # Startup
    logger.info("=" * 60)
    logger.info("Запуск API сервера...")
    logger.info("=" * 60)
    
    try:
        from app.db.init_db import init_db
        logger.info("Инициализация базы данных для API...")
        await init_db()
        logger.info("✅ База данных инициализирована")
    except Exception as e:
        logger.error(f"❌ Ошибка при инициализации базы данных: {e}", exc_info=True)
        logger.error("Проверьте переменную DATABASE_URL в Railway")
        # Не поднимаем исключение, чтобы увидеть другие ошибки
    
    logger.info("✅ API сервер готов к работе")
    logger.info("=" * 60)
    
    yield
    
    # Shutdown
    logger.info("Остановка API сервера...")


app = FastAPI(
    title="Fitness Bot API",
    description="API для работы с базой данных: пользователи, программы тренировок, упражнения, подходы",
    version="2.0.0",
    lifespan=lifespan
)

# Настройка CORS (разрешаем все источники для простоты)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(api_router, prefix="/api", tags=["api"])


@app.get("/")
async def root():
    """Корневой endpoint."""
    return {
        "message": "Fitness Bot API",
        "version": "2.0.0",
        "endpoints": {
            "users": "/api/users",
            "programs": "/api/programs",
            "exercises": "/api/exercises",
            "session-runs": "/api/session-runs",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Проверка здоровья API."""
    return {"status": "ok"}

