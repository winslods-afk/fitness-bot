"""Запуск API сервера отдельно от бота."""
import asyncio
import logging
import uvicorn
from app.db.init_db import init_db
from app.api.main import app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def startup():
    """Инициализация при запуске API сервера."""
    logger.info("Инициализация базы данных для API...")
    await init_db()
    logger.info("База данных инициализирована")


@app.on_event("startup")
async def startup_event():
    """Событие запуска FastAPI приложения."""
    await startup()


if __name__ == "__main__":
    # Запуск API сервера
    # Railway автоматически устанавливает переменную PORT
    import os
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "app.api.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

