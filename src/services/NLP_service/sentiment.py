"""
Модуль анализа тональности текста.
Использует cointegrated/rubert-tiny-sentiment-balanced для русского языка.
"""

import time
import logging
from typing import Dict, Any

import torch
from transformers import pipeline

from .exceptions import SentimentAnalysisError, ModelLoadError
from .models import SentimentResult


class SentimentAnalyzer:
    """
    Класс для анализа тональности текста.

    Использует легкую модель rubert-tiny-sentiment-balanced,
    специально обученную на русском языке.
    """

    # Доступные модели с характеристиками
    AVAILABLE_MODELS = {
        "rubert-tiny-sentiment": {
            "name": "cointegrated/rubert-tiny-sentiment-balanced",
            "size_mb": 69,
            "languages": ["ru"],
            "labels": ["positive", "negative", "neutral"]
        }
    }

    def __init__(self,
                 model_name: str = "cointegrated/rubert-tiny-sentiment-balanced",
                 device: Optional[str] = None,
                 use_gpu: bool = True):
        """
        Инициализация анализатора тональности.

        Args:
            model_name: название модели
            device: устройство для вычислений
            use_gpu: использовать ли GPU (если доступен)

        Raises:
            ModelLoadError: если не удалось загрузить модель
        """
        self.model_name = model_name
        self.logger = logging.getLogger(__name__)

        # Определяем устройство
        if device is None:
            self.device = "cuda" if (use_gpu and torch.cuda.is_available()) else "cpu"
        else:
            self.device = device

        self.logger.info(f"Loading sentiment model on {self.device}...")

        try:
            # Загружаем модель через pipeline
            self.pipeline = pipeline(
                "sentiment-analysis",
                model=model_name,
                device=self.device,
                truncation=True,
                max_length=512
            )
            self.logger.info("Sentiment model loaded successfully")

        except Exception as e:
            self.logger.error(f"Failed to load sentiment model: {e}")
            raise ModelLoadError(f"Failed to load sentiment model: {e}") from e

    async def analyze(self, text: str) -> SentimentResult:
        """
        Анализирует тональность текста.

        Args:
            text: текст для анализа

        Returns:
            SentimentResult: результат анализа

        Raises:
            SentimentAnalysisError: если анализ не удался
        """
        try:
            start_time = time.time()

            # Обрезаем длинный текст
            if len(text) > 1000:
                text = text[:1000]
                self.logger.debug(f"Text truncated to 1000 chars")

            # Анализ
            result = self.pipeline(text)[0]

            # Конвертируем в нашу модель
            sentiment_result = SentimentResult(
                label=result['label'],
                score=float(result['score'])
            )

            processing_time = (time.time() - start_time) * 1000
            self.logger.debug(f"Sentiment analysis took {processing_time:.2f}ms")

            return sentiment_result

        except Exception as e:
            self.logger.error(f"Sentiment analysis failed: {e}")
            raise SentimentAnalysisError(f"Failed to analyze sentiment: {e}") from e

    def analyze_batch(self, texts: List[str]) -> List[SentimentResult]:
        """
        Анализирует тональность нескольких текстов (batch processing).

        Args:
            texts: список текстов

        Returns:
            список результатов анализа
        """
        try:
            results = self.pipeline(texts, truncation=True, max_length=512)
            return [SentimentResult(label=r['label'], score=float(r['score']))
                    for r in results]
        except Exception as e:
            self.logger.error(f"Batch sentiment analysis failed: {e}")
            raise SentimentAnalysisError(f"Batch analysis failed: {e}") from e

    def get_model_info(self) -> Dict[str, Any]:
        """Возвращает информацию о модели."""
        return {
            "model_name": self.model_name,
            "device": self.device,
            "labels": self.AVAILABLE_MODELS["rubert-tiny-sentiment"]["labels"],
            "languages": self.AVAILABLE_MODELS["rubert-tiny-sentiment"]["languages"]
        }