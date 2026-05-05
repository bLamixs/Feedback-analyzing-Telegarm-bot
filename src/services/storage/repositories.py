"""
Репозитории для CRUD операций с БД.
Инкапсулируют логику запросов к конкретным таблицам.
"""

from typing import Optional, List

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User, Message, AnalysisResult, ErrorLog
from .exceptions import UserNotFoundError, MessageNotFoundError


class UserRepository:
    """Репозиторий для работы с пользователями."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create(self, telegram_id: int, username: str = None,
                            first_name: str = None, last_name: str = None) -> User:
        """Получает пользователя по telegram_id или создаёт нового."""
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()

        if user is None:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name
            )
            self.session.add(user)
            await self.session.flush()

        return user

    async def get_by_telegram_id(self, telegram_id: int) -> User:
        """Возвращает пользователя по telegram_id."""
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        if user is None:
            raise UserNotFoundError(f"User with telegram_id {telegram_id} not found")
        return user


class MessageRepository:
    """Репозиторий для работы с сообщениями."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: int, message_type: str,
                     content_text: str = None, recognized_text: str = None,
                     audio_path: str = None) -> Message:
        """Создаёт новое сообщение."""
        message = Message(
            user_id=user_id,
            message_type=message_type,
            content_text=content_text,
            recognized_text=recognized_text,
            audio_path=audio_path
        )
        self.session.add(message)
        await self.session.flush()
        return message

    async def get_by_id(self, message_id: int) -> Message:
        """Возвращает сообщение по ID с загрузкой связанных данных."""
        result = await self.session.execute(
            select(Message)
            .where(Message.id == message_id)
        )
        message = result.scalar_one_or_none()
        if message is None:
            raise MessageNotFoundError(f"Message {message_id} not found")
        return message

    async def get_by_user(self, user_id: int, limit: int = 50, offset: int = 0) -> List[Message]:
        """Возвращает список сообщений пользователя с пагинацией."""
        result = await self.session.execute(
            select(Message)
            .where(Message.user_id == user_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()

    async def get_stats_by_user(self, user_id: int) -> dict:
        """Статистика по сообщениям пользователя."""
        result = await self.session.execute(
            select(
                func.count(Message.id).label("total"),
                func.count(Message.audio_path).label("voice_count"),
                func.count(Message.content_text).label("text_count")
            )
            .where(Message.user_id == user_id)
        )
        row = result.one()
        return {
            "total_messages": row.total,
            "voice_messages": row.voice_count,
            "text_messages": row.text_count
        }


class AnalysisRepository:
    """Репозиторий для работы с результатами анализа."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, message_id: int, sentiment: str, sentiment_score: float,
                     topic: str, topic_score: float, intent: str,
                     has_help_request: bool, summary: str, processing_time_ms: int) -> AnalysisResult:
        """Создаёт результат анализа для сообщения."""
        analysis = AnalysisResult(
            message_id=message_id,
            sentiment=sentiment,
            sentiment_score=sentiment_score,
            topic=topic,
            topic_score=topic_score,
            intent=intent,
            has_help_request=has_help_request,
            summary=summary,
            processing_time_ms=processing_time_ms
        )
        self.session.add(analysis)
        await self.session.flush()
        return analysis

    async def get_by_message_id(self, message_id: int) -> Optional[AnalysisResult]:
        """Возвращает анализ по ID сообщения."""
        result = await self.session.execute(
            select(AnalysisResult).where(AnalysisResult.message_id == message_id)
        )
        return result.scalar_one_or_none()


class ErrorLogRepository:
    """Репозиторий для логирования ошибок."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, error_type: str, error_message: str, message_id: int = None) -> ErrorLog:
        """Сохраняет ошибку в лог."""
        error_log = ErrorLog(
            error_type=error_type,
            error_message=error_message,
            message_id=message_id
        )
        self.session.add(error_log)
        await self.session.flush()
        return error_log