"""
Основной NLP сервис для анализа текста.
Объединяет анализ тональности, классификацию темы и определение намерения.
"""

import time
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from .sentiment import SentimentAnalyzer
from .topic import TopicClassifier
from .intent import IntentDetector
from .models import AnalysisResult
from .exceptions import NLPError
from .utils import clean_text


class NLPAnalysisService:
    """
    Главный сервис NLP анализа.

    Объединяет:
    - Анализ тональности (rubert-tiny-sentiment)
    - Классификацию темы (sentence-transformers)
    - Определение намерения (rule-based + ML)
    """

    def __init__(self,
                 use_gpu: bool = True,
                 sentiment_model: str = "cointegrated/rubert-tiny-sentiment-balanced",
                 topic_model: str = "paraphrase-multilingual-MiniLM-L12-v2",
                 custom_topics: Optional[list] = None):
        """
        Инициализация NLP сервиса.

        Args:
            use_gpu: использовать ли GPU
            sentiment_model: модель для тональности
            topic_model: модель для тем
            custom_topics: пользовательские темы
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing NLP Analysis Service...")

        try:
            # Инициализируем компоненты
            self.sentiment = SentimentAnalyzer(
                model_name=sentiment_model,
                use_gpu=use_gpu
            )

            self.topic = TopicClassifier(
                model_name=topic_model,
                topics=custom_topics
            )

            self.intent = IntentDetector(use_ml_fallback=False)

            self.logger.info("NLP Analysis Service initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize NLP service: {e}")
            raise NLPError(f"Failed to initialize NLP service: {e}") from e

    async def analyze(self, text: str, context: Optional[Dict] = None) -> AnalysisResult:
        """
        Полный анализ текста.

        Args:
            text: текст для анализа
            context: дополнительный контекст

        Returns:
            AnalysisResult: полные результаты анализа

        Raises:
            NLPError: если анализ не удался
        """
        start_time = time.time()

        try:
            # Очищаем текст
            cleaned_text = clean_text(text, remove_punctuation=False)

            self.logger.debug(f"Analyzing text: {cleaned_text[:50]}...")

            # Параллельно выполняем все анализы
            import asyncio

            sentiment_task = self.sentiment.analyze(cleaned_text)
            topic_task = self.topic.classify(cleaned_text)
            intent_task = self.intent.detect(cleaned_text, context or {})

            # Ждем завершения всех задач
            sentiment_result, topic_result, intent_result = await asyncio.gather(
                sentiment_task, topic_task, intent_task
            )

            # Формируем полный результат
            processing_time = (time.time() - start_time) * 1000

            result = AnalysisResult(
                text=text,
                text_length=len(text),
                sentiment=sentiment_result,
                topic=topic_result,
                intent=intent_result,
                processing_time_ms=processing_time
            )

            self.logger.info(f"Analysis completed in {processing_time:.2f}ms")
            self.logger.debug(f"Result: {result.json()}")

            return result

        except Exception as e:
            self.logger.error(f"Analysis failed: {e}")
            raise NLPError(f"Failed to analyze text: {e}") from e

    async def analyze_batch(self, texts: list) -> list:
        """
        Анализ нескольких текстов.

        Args:
            texts: список текстов

        Returns:
            список результатов анализа
        """
        results = []
        for text in texts:
            result = await self.analyze(text)
            results.append(result)
        return results

    def get_service_info(self) -> Dict[str, Any]:
        """Возвращает информацию о сервисе."""
        return {
            "sentiment": self.sentiment.get_model_info(),
            "topic": self.topic.get_model_info(),
            "intent": {
                "supported_intents": self.intent.get_supported_intents(),
                "method": "rule-based + ML"
            }
        }