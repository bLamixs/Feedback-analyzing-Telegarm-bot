from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from src.config.settings import settings

# Базовый класс для моделей
Base = declarative_base()

# Создание асинхронного движка
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,  # Лучше вынести в настройки: True для отладки, False для прода
    future=True,
    pool_pre_ping=True,  # Проверка соединения перед использованием
    pool_size=settings.DB_POOL_SIZE,  # Размер пула (можно в настройках)
    max_overflow=settings.DB_MAX_OVERFLOW,  # Дополнительные соединения при пике
    pool_recycle=3600,  # Пересоздавать соединения каждый час
)

# Фабрика сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)