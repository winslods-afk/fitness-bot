"""Инициализация и настройка бота."""
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import BOT_TOKEN
from app.db.init_db import init_db, get_session
from app.handlers import start, add_program, delete_program, training, stats

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def setup_database():
    """Инициализация базы данных."""
    await init_db()
    logger.info("База данных готова к работе")


def setup_handlers(dp: Dispatcher):
    """Регистрация всех обработчиков."""
    # Системные обработчики (команды) - высокий приоритет
    dp.include_router(start.router)
    dp.include_router(add_program.router)
    dp.include_router(delete_program.router)
    # Тренировка перед статистикой, чтобы обработчик select_day_ срабатывал правильно
    dp.include_router(training.router)
    dp.include_router(stats.router)
    
    # AI обработчики
    from app.handlers import ai_handler, ai_program
    # Обработчик создания программ через AI (высокий приоритет)
    dp.include_router(ai_program.router)
    # Обработчик свободных сообщений (низкий приоритет)
    dp.include_router(ai_handler.router)


async def create_bot() -> tuple[Bot, Dispatcher]:
    """Создание и настройка бота."""
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    dp = Dispatcher(storage=MemoryStorage())
    
    # Middleware для работы с БД
    from aiogram import BaseMiddleware
    from typing import Callable, Dict, Any, Awaitable
    
    class DatabaseMiddleware(BaseMiddleware):
        async def __call__(
            self,
            handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
            event: Any,
            data: Dict[str, Any]
        ) -> Any:
            async for session in get_session():
                data["session"] = session
                try:
                    result = await handler(event, data)
                    return result
                finally:
                    await session.close()
    
    # Регистрируем middleware для всех типов обновлений
    dp.message.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())
    
    setup_handlers(dp)
    
    return bot, dp

