"""Точка входа в приложение."""
import asyncio
import logging
from app.bot import create_bot, setup_database

logger = logging.getLogger(__name__)


async def main():
    """Главная функция запуска бота."""
    logger.info("Запуск бота...")
    
    # Инициализация базы данных
    await setup_database()
    
    # Создание бота и диспетчера
    bot, dp = await create_bot()
    
    # Запуск бота
    logger.info("Бот запущен и готов к работе")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}", exc_info=True)

