"""
Пакет конфигурации: настройки и логгер.
"""

from .settings import settings
from .logger import setup_logging, get_logger

__all__ = ["settings", "setup_logging", "get_logger"]