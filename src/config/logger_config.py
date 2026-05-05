"""
Настройка логирования для всего приложения.
"""

import logging
import sys
from pathlib import Path

from .settings import settings


def setup_logging() -> None:
    """
    Инициализирует логирование:
    - вывод в консоль (цветной, если поддерживается)
    - запись в файл data/logs/app.log
    - ротация логов (по размеру)
    """

    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Очищаем существующие обработчики (чтобы не дублировать при перезапуске)
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Обработчик для консоли
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(log_format, datefmt=date_format)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # Обработчик для файла (с ротацией)
    logs_dir = settings.BASE_DIR / "data" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / "app.log"

    try:
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(log_format, datefmt=date_format)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:

        root_logger.warning(f"Could not set up file logging: {e}")


    logging.getLogger("aiogram").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    if settings.DEBUG:
        root_logger.info("Logging initialized in DEBUG mode")
    else:
        root_logger.info("Logging initialized")


def get_logger(name: str) -> logging.Logger:
    """
    Возвращает логгер с указанным именемс
    """
    return logging.getLogger(name)