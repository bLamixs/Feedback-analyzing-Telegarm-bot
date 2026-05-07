"""
Точка входа в бота
Запускает Tg бота со всеми сервисами
"""

import asyncio
import logging
import sys

from aiogram import Bot
from src.config import settings, logger_config
from src.core import orchestrator
from src.services.storage import storage


async def main():


    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting Cyber-Secretary bot...")


    if not settings.Bot_TOKEN:
        if not settings.BOT_TOKEN:
            logger.error("BOT_TOKEN not set in environment")
            sys.exit(1)

            # 3. Инициализация сервисов
        logger.info("Initializing services...")

        storage = StorageService()
        await storage.initialize()

        # Оркестратор сам создаст STT, NLP, суммаризацию
        orchestrator = Orchestrator(
            storage_service=storage,
            config=settings.orchestrator_config
        )

        # Проверка здоровья (опционально)
        health = await orchestrator.health_check()
        if not health:
            logger.warning("Health check failed, but continuing anyway...")

        # 4. Создание бота и диспетчера
        bot = Bot(token=settings.BOT_TOKEN)
        dp = setup_dispatcher()

        # 5. Передаём оркестратор в хендлеры (можно через глобальную переменную или middleware)
        #    Лучше через middleware или регистрацию в state.
        #    Упрощённо: сделаем его доступным через функцию get_orchestrator.
        #    Для простоты создадим контекст.
        from bot.handlers.text_handler import set_orchestrator
        from bot.handlers.voice_handler import set_orchestrator as set_voice_orchestrator

        set_orchestrator(orchestrator)
        set_voice_orchestrator(orchestrator)

        # 6. Запуск поллинга
        logger.info("Starting polling...")
        try:
            await dp.start_polling(bot, allowed_updates=["message", "callback_query"])
        finally:
            # 7. Корректное завершение
            await storage.close()
            await bot.session.close()
            logger.info("Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())

