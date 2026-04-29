"""
Модели данных для оркестратора.
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any


class UserContext(BaseModel):
    """Контекст пользователя"""
    user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    chat_id: int


class ProcessedMessage(BaseModel):
    """Результат обработки сообщения"""
    message_id: int
    user_id: int
    message_type: str  # 'text' or 'voice'
    original_text: Optional[str] = None
    recognized_text: Optional[str] = None  # для голоса
    sentiment: str
    sentiment_score: float
    topic: str
    topic_score: float
    intent: str
    has_help_request: bool
    summary: str
    processing_time_ms: float
    created_at: datetime = datetime.now()