from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text, Float, BigInteger
from sqlalchemy import CheckConstraint, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

# Исправьте путь на актуальный для вашего проекта
from src.core.database import Base  # или from core.database import Base


class User(Base):
    """
    Пользователь Telegram
    """
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    messages: Mapped[list["Message"]] = relationship(
        "Message", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"User(id={self.id}, telegram_id={self.telegram_id}, username={self.username})"


class Message(Base):
    """
    Сообщение от пользователя
    """
    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Тип сообщения: 'text' или 'voice'
    message_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default='text'
    )

    # Текст сообщения (если текстовое или результат распознавания голоса)
    content_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Путь к аудиофайлу (если голосовое)
    audio_path: Mapped[str | None] = mapped_column(String(512), unique=False, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="messages")
    analysis: Mapped["AnalysisResult | None"] = relationship(
        "AnalysisResult",
        back_populates="message",
        uselist=False,  # one-to-one
        cascade="all, delete-orphan"
    )
    error_logs: Mapped[list["ErrorLog"]] = relationship(
        "ErrorLog",
        back_populates="message",
        cascade="all, delete-orphan"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "message_type IN ('text', 'voice')",
            name="check_message_type_valid"
        ),
    )

    def __repr__(self) -> str:
        return f"Message(id={self.id}, type={self.message_type}, user_id={self.user_id})"


class AnalysisResult(Base):
    """
    Результат анализа сообщения
    """
    __tablename__ = 'analysis_results'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # One-to-one связь с Message
    message_id: Mapped[int] = mapped_column(
        ForeignKey("messages.id", ondelete="CASCADE"),
        unique=True,  # гарантирует one-to-one
        nullable=False,
        index=True
    )

    # Результаты анализа тональности
    sentiment: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="positive/negative/neutral"
    )
    sentiment_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Confidence score (0-1)"
    )

    # Тема сообщения (классификация)
    topic: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True,
        comment="tech_support/feedback/spam/etc"
    )

    # Намерение пользователя
    intent: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="help_request/complaint/question/etc"
    )

    # Краткое содержание (саммари)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Метаданные обработки
    processing_time_ms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Processing time in milliseconds"
    )

    # Дополнительные данные в JSON формате (для гибкости)
    extra_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    message: Mapped["Message"] = relationship("Message", back_populates="analysis")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "sentiment IN ('positive', 'negative', 'neutral')",
            name="check_sentiment_valid"
        ),
    )

    def __repr__(self) -> str:
        return f"AnalysisResult(id={self.id}, message_id={self.message_id}, sentiment={self.sentiment})"


class ErrorLog(Base):
    """
    Логирование ошибок
    """
    __tablename__ = 'error_logs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Связь с сообщением (может быть NULL, если ошибка до создания сообщения)
    message_id: Mapped[int | None] = mapped_column(
        ForeignKey("messages.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Тип ошибки
    error_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="stt_error/nlp_error/db_error/etc"
    )

    # Текст ошибки
    error_message: Mapped[str] = mapped_column(Text, nullable=False)

    # Детали ошибки (JSON для stack trace и доп. информации)
    error_details: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    # Relationships
    message: Mapped["Message | None"] = relationship("Message", back_populates="error_logs")

    def __repr__(self) -> str:
        return f"ErrorLog(id={self.id}, type={self.error_type}, message_id={self.message_id})"


# Дополнительная таблица для хранения статистики (опционально)
class ProcessingStats(Base):
    """
    Статистика обработки для мониторинга
    """
    __tablename__ = 'processing_stats'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )

    # Общая статистика
    total_messages: Mapped[int] = mapped_column(Integer, default=0)
    total_voice: Mapped[int] = mapped_column(Integer, default=0)
    total_text: Mapped[int] = mapped_column(Integer, default=0)

    # Статистика по тональности
    positive_count: Mapped[int] = mapped_column(Integer, default=0)
    negative_count: Mapped[int] = mapped_column(Integer, default=0)
    neutral_count: Mapped[int] = mapped_column(Integer, default=0)

    # Среднее время обработки
    avg_processing_time: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Статистика по темам (JSON для гибкости)
    topics_stats: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


