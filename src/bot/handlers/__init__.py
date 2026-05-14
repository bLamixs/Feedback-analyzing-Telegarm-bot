"""Обработчики команд и сообщений бота."""

from .commands import router as commands_router
from .text_handler import router as text_router
from .audio_handler  import router as voice_router

__all__ = [
    "commands_router",
    "text_router",
    "voice_router",
]