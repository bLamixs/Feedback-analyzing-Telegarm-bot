"""
Подключение к базе данных.
Создание engine, сессий, управление подключением.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)
from sqlalchemy.orm import declarative_base

from config import settings

# Базовый класс для моделей
Base = declarative_base()


def create_engine():
    """Создает асинхронный engine для подключения к БД."""
    return create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
    )


# Глобальный engine
_engine = None
_async_session_maker = None


def get_engine():
    """Возвращает engine (ленивая инициализация)."""
    global _engine
    if _engine is None:
        _engine = create_engine()
    return _engine


def get_session_maker():
    """Возвращает фабрику сессий."""
    global _async_session_maker
    if _async_session_maker is None:
        _async_session_maker = async_sessionmaker(
            get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _async_session_maker


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для получения сессии БД.
    Используется в репозиториях и сервисах.
    """
    session_maker = get_session_maker()
    async with session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Создаёт все таблицы в БД (для первого запуска)."""
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Закрывает соединение с БД (при завершении приложения)."""
    engine = get_engine()
    await engine.dispose()