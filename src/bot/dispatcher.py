"""
Настройка диспетчера aiogram.
Подключает все роутеры с обработчиками.
"""

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.handlers import commands, text_handler, voice_handler, admin


def setup_dispatcher() -> Dispatcher:
    """Создаёт и настраивает диспетчер."""
    dp = Dispatcher(storage=MemoryStorage())

    # Регистрируем роутеры (именно такой порядок)
    dp.include_router(commands.router)      # /start, /help, /info
    dp.include_router(text_handler.router)  # обычные текстовые сообщения
    dp.include_router(voice_handler.router) # голосовые сообщения

    return dp