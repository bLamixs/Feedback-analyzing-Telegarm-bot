"""
Модели для сервиса NLP анализа текста
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

class SentimentResult(BaseModel):
    """Результат анализа тональности """
    label: str = Field(..., description = "positive/negative/neutral")
    score: float = Field(..., ge= 0, le=1, description = "Уверенность модели")

    class Config:
        schema_extra = {
            "examples": {
                "label": "negative",
                "score": 0.98,
            }
        }

class TopicResult(BaseModel):
    "Результат классификации темы"
    topic:str = Field(..., description="tech/support/feedback/spam/etc")
    score: float = Field(..., ge=0,le=1,description = "Уверенность модели")
    all_scores:Optional[Dict[str, float]] = Field(None, description="Все оценки")

    class Config:
        schema_extra = {
            "examples": {
                "topic": "tech_support",
                "score": 0.87,
                "all_scores": {
                    "tech_support": 0.87,
                    "feedback": 0.12,
                    "spam": 0.01
                }
            }
        }
class IntentResult(BaseModel):
    """Результат определения намерения"""
    intent:str =  Field(..., description="help_request/complaint/question/etc")
    confidence: float = Field(..., ge=0, le=1, description="Уверенность")
    has_help_request: bool = Field(False, description="Есть ли просьба о помощи")

    class Config:
        schema_extra = {
            "example": {
                "intent": "help_request",
                "confidence": 0.95,
                "has_help_request": True
            }
        }


class AnalysisResult(BaseModel):
    """Полный результат NLP анализа"""
    text: str = Field(..., description="Исходный текст")
    text_length: int = Field(..., description="Длина текста в символах")

    sentiment: SentimentResult
    topic: TopicResult
    intent: IntentResult

    processing_time_ms: float = Field(..., description="Время обработки в мс")
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        schema_extra = {
            "example": {
                "text": "Все сломалось, чините быстрее!",
                "text_length": 30,
                "sentiment": {
                    "label": "negative",
                    "score": 0.98
                },
                "topic": {
                    "topic": "tech_support",
                    "score": 0.87
                },
                "intent": {
                    "intent": "help_request",
                    "confidence": 0.95,
                    "has_help_request": True
                },
                "processing_time_ms": 156.7
            }
        }