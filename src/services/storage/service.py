"""
Storage Service — фасад для работы с БД.
Объединяет все репозитории и предоставляет единый интерфейс для оркестратора.
"""

import logging
from typing import Optional, List

from .database import get_session, init_db, close_db
from .repositories import UserRepository, MessageRepository, AnalysisRepository, ErrorLogRepository
from .exceptions import StorageError, UserNotFoundError
from src.core.models import ProcessedMessage, UserContext


class StorageService:
    """
    Сервис для работы с хранилищем данных.

    Инкапсулирует все операции с БД и предоставляет простой API для оркестратора.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._initialized = False

    async def initialize(self) -> None:
        """Инициализация БД (создание таблиц при первом запуске)."""
        if not self._initialized:
            await init_db()
            self._initialized = True
            self.logger.info("Storage service initialized")

    async def close(self) -> None:
        """Закрытие соединения с БД."""
        await close_db()
        self.logger.info("Storage service closed")

    # ========================
    # Основные методы для оркестратора
    # ========================

    async def save_message(self, processed: ProcessedMessage, user_ctx: UserContext) -> None:
        """
        Сохраняет обработанное сообщение в БД.

        Args:
            processed: результат обработки сообщения
            user_ctx: контекст пользователя
        """
        async for session in get_session():
            try:
                # 1. Получаем или создаём пользователя
                user_repo = UserRepository(session)
                user = await user_repo.get_or_create(
                    telegram_id=user_ctx.user_id,
                    username=user_ctx.username,
                    first_name=user_ctx.first_name,
                    last_name=user_ctx.last_name
                )

                # 2. Создаём запись о сообщении
                message_repo = MessageRepository(session)
                message = await message_repo.create(
                    user_id=user.id,
                    message_type=processed.message_type,
                    content_text=processed.original_text,
                    recognized_text=processed.recognized_text,
                    audio_path=None
                )

                # 3. Создаём запись о результатах анализа
                analysis_repo = AnalysisRepository(session)
                await analysis_repo.create(
                    message_id=message.id,
                    sentiment=processed.sentiment,
                    sentiment_score=processed.sentiment_score,
                    topic=processed.topic,
                    topic_score=processed.topic_score,
                    intent=processed.intent,
                    has_help_request=processed.has_help_request,
                    summary=processed.summary,
                    processing_time_ms=int(processed.processing_time_ms)
                )

                # 4. Подтверждаем транзакцию
                await session.commit()
                self.logger.debug(f"Saved message {processed.message_id} for user {user_ctx.user_id}")

            except Exception as e:
                await session.rollback()
                self.logger.error(f"Failed to save message: {e}", exc_info=True)
                raise StorageError(f"Failed to save message: {e}")

    async def get_user_history(self, telegram_id: int, limit: int = 10) -> List[dict]:
        """
        Возвращает историю сообщений пользователя.

        Args:
            telegram_id: Telegram ID пользователя
            limit: количество последних сообщений

        Returns:
            список словарей с данными сообщений и анализа
        """
        async for session in get_session():
            try:
                # Получаем пользователя
                user_repo = UserRepository(session)
                user = await user_repo.get_by_telegram_id(telegram_id)

                # Получаем сообщения
                message_repo = MessageRepository(session)
                messages = await message_repo.get_by_user(user.id, limit=limit)

                result = []
                for msg in messages:
                    # Загружаем анализ для каждого сообщения
                    analysis_repo = AnalysisRepository(session)
                    analysis = await analysis_repo.get_by_message_id(msg.id)

                    result.append({
                        "message_id": msg.id,
                        "message_type": msg.message_type,
                        "text": msg.recognized_text or msg.content_text,
                        "created_at": msg.created_at.isoformat(),
                        "analysis": {
                            "sentiment": analysis.sentiment if analysis else None,
                            "topic": analysis.topic if analysis else None,
                            "intent": analysis.intent if analysis else None,
                            "summary": analysis.summary if analysis else None
                        } if analysis else None
                    })

                return result

            except UserNotFoundError:
                return []  # Пользователь ещё не писал боту
            except Exception as e:
                self.logger.error(f"Failed to get user history: {e}", exc_info=True)
                raise StorageError(f"Failed to get user history: {e}")

    async def log_error(self, error_type: str, error_message: str, message_id: int = None) -> None:
        """
        Логирует ошибку в БД.

        Args:
            error_type: тип ошибки
            error_message: текст ошибки
            message_id: ID сообщения (если есть)
        """
        async for session in get_session():
            try:
                log_repo = ErrorLogRepository(session)
                await log_repo.create(error_type, error_message, message_id)
                await session.commit()
            except Exception as e:
                self.logger.error(f"Failed to log error: {e}")
                # Не поднимаем исключение, чтобы не блокировать основную логику

    async def get_user_stats(self, telegram_id: int) -> dict:
        """
        Возвращает статистику по пользователю.

        Args:
            telegram_id: Telegram ID пользователя

        Returns:
            словарь со статистикой
        """
        async for session in get_session():
            try:
                user_repo = UserRepository(session)
                user = await user_repo.get_by_telegram_id(telegram_id)

                message_repo = MessageRepository(session)
                stats = await message_repo.get_stats_by_user(user.id)

                return stats

            except UserNotFoundError:
                return {"total_messages": 0, "voice_messages": 0, "text_messages": 0}
            except Exception as e:
                self.logger.error(f"Failed to get user stats: {e}", exc_info=True)
                raise StorageError(f"Failed to get user stats: {e}")