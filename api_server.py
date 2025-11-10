"""Запуск API сервера отдельно от бота."""
import logging
import os
import sys

# Настройка логирования ДО импортов
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

try:
    import uvicorn
except ImportError:
    logger.error("❌ uvicorn не установлен. Установите: pip install uvicorn[standard]")
    sys.exit(1)

if __name__ == "__main__":
    # Запуск API сервера
    # Railway автоматически устанавливает переменную PORT
    port = int(os.getenv("PORT", 8000))
    
    logger.info("=" * 60)
    logger.info("Запуск API сервера...")
    logger.info(f"Порт: {port}")
    logger.info("=" * 60)
    
    try:
        uvicorn.run(
            "app.api.main:app",
            host="0.0.0.0",
            port=port,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("Остановка сервера...")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка при запуске сервера: {e}", exc_info=True)
        sys.exit(1)

