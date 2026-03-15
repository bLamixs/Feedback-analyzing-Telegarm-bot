"""
Модуль классификации темы сообщения.
Использует sentence-transformers для zero-shot классификации.
"""

import time
import logging
from typing import List, Dict, Any, Optional

import torch
import numpy as np
from sentence_transformers import SentenceTransformer, util

from .exceptions import TopicClassificationError, ModelLoadError
from .models import TopicResult


class TopicClassifier:
    """
    Класс для классификации темы сообщения.

    Использует мультиязычную sentence-transformers модель для получения
    эмбеддингов и косинусное расстояние для zero-shot классификации.
    """

    # Предопределенные темы
    DEFAULT_TOPICS = [
        "техническая поддержка",
        "жалоба на сервис",
        "предложение по улучшению",
        "просто отзыв",
        "спам",
        "вопрос о услугах"
    ]

    # Английские версии для многоязычной модели
    DEFAULT_TOPICS_EN = [
        "technical support",
        "service complaint",
        "improvement suggestion",
        "general feedback",
        "spam",
        "service inquiry"
    ]

    def __init__(self,
                 model_name: str = "paraphrase-multilingual-MiniLM-L12-v2",
                 topics: Optional[List[str]] = None,
                 device: Optional[str] = None):
        """
        Инициализация классификатора тем.

        Args:
            model_name: название sentence-transformers модели
            topics: список тем для классификации
            device: устройство для вычислений

        Raises:
            ModelLoadError: если не удалось загрузить модель
        """
        self.model_name = model_name
        self.logger = logging.getLogger(__name__)

        # Определяем устройство
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        # Устанавливаем темы
        self.topics = topics or self.DEFAULT_TOPICS
        self.topics_en = self.DEFAULT_TOPICS_EN

        self.logger.info(f"Loading topic model on {self.device}...")

        try:
            # Загружаем модель
            self.model = SentenceTransformer(model_name, device=self.device)

            # Предвычисляем эмбеддинги тем
            self.topic_embeddings = self.model.encode(
                self.topics_en,
                convert_to_tensor=True,
                show_progress_bar=False
            )

            self.logger.info(f"Topic model loaded successfully. Topics: {self.topics}")

        except Exception as e:
            self.logger.error(f"Failed to load topic model: {e}")
            raise ModelLoadError(f"Failed to load topic model: {e}") from e

    async def classify(self, text: str, return_all_scores: bool = True) -> TopicResult:
        """
        Классифицирует тему сообщения.

        Args:
            text: текст для классификации
            return_all_scores: возвращать ли все оценки

        Returns:
            TopicResult: результат классификации

        Raises:
            TopicClassificationError: если классификация не удалась
        """
        try:
            start_time = time.time()

            # Получаем эмбеддинг текста
            text_embedding = self.model.encode(
                text,
                convert_to_tensor=True,
                show_progress_bar=False
            )

            # Вычисляем косинусное сходство со всеми темами
            scores = util.cos_sim(text_embedding, self.topic_embeddings)[0]

            # Конвертируем в numpy для удобства
            scores_np = scores.cpu().numpy()

            # Находим лучшую тему
            best_idx = np.argmax(scores_np)
            best_score = float(scores_np[best_idx])
            best_topic = self.topics[best_idx]

            # Формируем результат
            result = TopicResult(
                topic=best_topic,
                score=best_score
            )

            if return_all_scores:
                result.all_scores = {
                    self.topics[i]: float(scores_np[i])
                    for i in range(len(self.topics))
                }

            processing_time = (time.time() - start_time) * 1000
            self.logger.debug(f"Topic classification took {processing_time:.2f}ms")

            return result

        except Exception as e:
            self.logger.error(f"Topic classification failed: {e}")
            raise TopicClassificationError(f"Failed to classify topic: {e}") from e

    async def classify_batch(self, texts: List[str]) -> List[TopicResult]:
        """
        Классифицирует темы нескольких сообщений.

        Args:
            texts: список текстов

        Returns:
            список результатов классификации
        """
        try:
            # Получаем эмбеддинги всех текстов
            text_embeddings = self.model.encode(
                texts,
                convert_to_tensor=True,
                show_progress_bar=False
            )

            # Вычисляем сходство со всеми темами
            all_scores = util.cos_sim(text_embeddings, self.topic_embeddings)

            results = []
            for scores in all_scores:
                scores_np = scores.cpu().numpy()
                best_idx = np.argmax(scores_np)
                results.append(TopicResult(
                    topic=self.topics[best_idx],
                    score=float(scores_np[best_idx])
                ))

            return results

        except Exception as e:
            self.logger.error(f"Batch topic classification failed: {e}")
            raise TopicClassificationError(f"Batch classification failed: {e}") from e

    def add_topic(self, topic: str, topic_en: str):
        """
        Добавляет новую тему для классификации.

        Args:
            topic: тема на русском
            topic_en: тема на английском
        """
        self.topics.append(topic)
        self.topics_en.append(topic_en)

        # Пересчитываем эмбеддинги
        self.topic_embeddings = self.model.encode(
            self.topics_en,
            convert_to_tensor=True,
            show_progress_bar=False
        )
        self.logger.info(f"Added new topic: {topic}")

    def get_model_info(self) -> Dict[str, Any]:
        """Возвращает информацию о модели."""
        return {
            "model_name": self.model_name,
            "device": self.device,
            "topics": self.topics,
            "embedding_dim": self.model.get_sentence_embedding_dimension()
        }