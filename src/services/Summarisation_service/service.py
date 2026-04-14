"""
Сервис экстрактивной суммаризации текста.
Использует библиотеку Sumy с различными алгоритмами.
"""

import time
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer

from .exceptions import SummarizationError, TextTooShortError, AlgorithmNotFoundError
from .algorithms import ALGORITHMS, get_algorithm, list_algorithms
from .utils import estimate_optimal_sentences_count, get_text_stats


@dataclass
class SummarizationResult:
    """Результат суммаризации"""
    summary: str
    original_length: int
    summary_length: int
    sentences_count: int
    algorithm: str
    processing_time_ms: float
    stats: Dict[str, Any]


class SummarizationService:
    """
    Сервис экстрактивной суммаризации текста.

    Поддерживаемые алгоритмы:
    - lsa: Latent Semantic Analysis (рекомендуется)
    - textrank: TextRank графовый алгоритм
    - luhn: частотный анализ
    - edmundson: с учетом позиции и ключевых слов
    """

    def __init__(self,
                 default_algorithm: str = "lsa",
                 language: str = "russian",
                 min_sentences: int = 1,
                 max_sentences: int = 5):
        """
        Инициализация сервиса суммаризации.

        Args:
            default_algorithm: алгоритм по умолчанию
            language: язык текста
            min_sentences: минимальное количество предложений
            max_sentences: максимальное количество предложений

        Raises:
            AlgorithmNotFoundError: если алгоритм не найден
        """
        self.logger = logging.getLogger(__name__)
        self.default_algorithm = default_algorithm
        self.language = language
        self.min_sentences = min_sentences
        self.max_sentences = max_sentences

        # Проверяем доступность алгоритма
        if default_algorithm not in ALGORITHMS:
            raise AlgorithmNotFoundError(
                f"Default algorithm '{default_algorithm}' not found. "
                f"Available: {list(ALGORITHMS.keys())}"
            )

        self.logger.info(f"SummarizationService initialized with {default_algorithm} algorithm")

    async def summarize(self,
                       text: str,
                       sentences_count: Optional[int] = None,
                       algorithm: Optional[str] = None,
                       **kwargs) -> SummarizationResult:
        """
        Суммаризирует текст.

        Args:
            text: исходный текст
            sentences_count: количество предложений в саммари
            algorithm: алгоритм суммаризации
            **kwargs: дополнительные параметры для алгоритма

        Returns:
            SummarizationResult: результат суммаризации

        Raises:
            TextTooShortError: текст слишком короткий
            SummarizationError: ошибка суммаризации
        """
        start_time = time.time()

        try:
            # Проверка текста
            if not text or len(text.split()) < 10:
                raise TextTooShortError("Text is too short for summarization")

            # Определяем алгоритм
            algo_name = algorithm or self.default_algorithm
            summarizer_class = get_algorithm(algo_name)

            # Создаем суммаризатор
            summarizer = summarizer_class()

            # Применяем дополнительные параметры
            for key, value in kwargs.items():
                if hasattr(summarizer, key):
                    setattr(summarizer, key, value)

            # Парсим текст
            parser = PlaintextParser.from_string(
                text,
                Tokenizer(self.language)
            )

            # Определяем количество предложений
            if sentences_count is None:
                sentences_count = estimate_optimal_sentences_count(
                    text,
                    self.min_sentences,
                    self.max_sentences
                )

            # Получаем саммари
            summary_sentences = summarizer(
                parser.document,
                sentences_count
            )

            # Объединяем предложения
            summary = " ".join(str(s) for s in summary_sentences)

            # Статистика
            processing_time = (time.time() - start_time) * 1000
            stats = get_text_stats(text)

            result = SummarizationResult(
                summary=summary,
                original_length=len(text),
                summary_length=len(summary),
                sentences_count=len(summary_sentences),
                algorithm=algo_name,
                processing_time_ms=processing_time,
                stats=stats
            )

            self.logger.debug(
                f"Summarization completed: {stats['sentence_count']} → "
                f"{len(summary_sentences)} sentences in {processing_time:.2f}ms"
            )

            return result

        except TextTooShortError:
            raise
        except Exception as e:
            self.logger.error(f"Summarization failed: {e}")
            raise SummarizationError(f"Failed to summarize text: {e}") from e

    async def summarize_simple(self, text: str, sentences_count: int = 3) -> str:
        """
        Упрощенный метод, возвращает только текст саммари.

        Args:
            text: исходный текст
            sentences_count: количество предложений

        Returns:
            str: краткое содержание
        """
        try:
            result = await self.summarize(text, sentences_count)
            return result.summary
        except TextTooShortError:
            return text  # Возвращаем оригинал если слишком коротко

    def compare_algorithms(self, text: str, sentences_count: int = 3) -> Dict[str, str]:
        """
        Сравнивает работу всех алгоритмов на одном тексте.

        Args:
            text: исходный текст
            sentences_count: количество предложений

        Returns:
            словарь {алгоритм: саммари}
        """
        import asyncio

        results = {}
        for algo_name in ALGORITHMS.keys():
            try:
                result = asyncio.run(self.summarize(
                    text,
                    sentences_count,
                    algorithm=algo_name
                ))
                results[algo_name] = result.summary
            except Exception as e:
                results[algo_name] = f"Error: {e}"

        return results

    def get_available_algorithms(self) -> Dict:
        """
        Возвращает информацию о доступных алгоритмах.
        """
        return list_algorithms()

    def get_service_info(self) -> Dict[str, Any]:
        """
        Возвращает информацию о сервисе.
        """
        return {
            "service": "Extractive Summarization",
            "default_algorithm": self.default_algorithm,
            "language": self.language,
            "min_sentences": self.min_sentences,
            "max_sentences": self.max_sentences,
            "available_algorithms": self.get_available_algorithms()
        }