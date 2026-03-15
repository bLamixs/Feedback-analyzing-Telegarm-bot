"""
Модуль определения намерения пользователя.
Комбинирует rule-based подход с ML для лучших результатов.
"""

import re
import time
import logging
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass

from .exceptions import IntentDetectionError
from .models import IntentResult
from .utils import contains_help_keywords, detect_urgency


@dataclass
class IntentPattern:
    """Шаблон для определения намерения"""
    name: str
    keywords: Set[str]
    priority: int = 1
    min_matches: int = 1


class IntentDetector:
    """
    Класс для определения намерения пользователя.

    Использует комбинацию:
    - Rule-based подход для быстрых детекций
    - Анализ ключевых слов
    - Контекст сообщения
    """

    # Предопределенные намерения и их паттерны
    INTENT_PATTERNS = {
        "help_request": IntentPattern(
            name="help_request",
            keywords={
                'помоги', 'помощь', 'спаси', 'срочно',
                'не работает', 'сломалось', 'ошибка',
                'help', 'please', 'emergency'
            },
            priority=3
        ),
        "complaint": IntentPattern(
            name="complaint",
            keywords={
                'плохо', 'ужасно', 'недоволен', 'отвратительно',
                'bad', 'terrible', 'awful', 'complaint',
                'не нравится', 'разочарован'
            },
            priority=2
        ),
        "question": IntentPattern(
            name="question",
            keywords={
                'как', 'почему', 'зачем', 'что', 'где',
                'когда', 'сколько', 'можно ли',
                'how', 'why', 'what', 'where', 'when'
            },
            priority=1
        ),
        "feedback": IntentPattern(
            name="feedback",
            keywords={
                'отзыв', 'мнение', 'предложение', 'идея',
                'feedback', 'suggestion', 'idea'
            },
            priority=1
        ),
        "greeting": IntentPattern(
            name="greeting",
            keywords={
                'привет', 'здравствуй', 'добрый', 'доброе',
                'hello', 'hi', 'good morning'
            },
            priority=1
        ),
        "spam": IntentPattern(
            name="spam",
            keywords={
                'купить', 'продать', 'скидка', 'акция',
                'buy', 'sell', 'discount', 'sale', 'offer'
            },
            priority=2
        )
    }

    def __init__(self, use_ml_fallback: bool = False):
        """
        Инициализация детектора намерений.

        Args:
            use_ml_fallback: использовать ли ML модель если rule-based не сработал
        """
        self.logger = logging.getLogger(__name__)
        self.use_ml_fallback = use_ml_fallback

        # Компилируем паттерны для быстрого поиска
        self.compiled_patterns = {}
        for intent_name, pattern in self.INTENT_PATTERNS.items():
            # Создаем регулярное выражение для поиска ключевых слов
            pattern_regex = r'\b(' + '|'.join(re.escape(k) for k in pattern.keywords) + r')\b'
            self.compiled_patterns[intent_name] = {
                'pattern': pattern,
                'regex': re.compile(pattern_regex, re.IGNORECASE)
            }

    async def detect(self, text: str, context: Optional[Dict] = None) -> IntentResult:
        """
        Определяет намерение пользователя.

        Args:
            text: текст сообщения
            context: дополнительный контекст (длина сообщения, предыдущие сообщения и т.д.)

        Returns:
            IntentResult: результат определения намерения

        Raises:
            IntentDetectionError: если определение не удалось
        """
        try:
            start_time = time.time()

            # Rule-based детекция
            intent, confidence = self._rule_based_detection(text)

            # Если rule-based не дал результата и есть ML fallback
            if intent == "unknown" and self.use_ml_fallback:
                intent, confidence = await self._ml_detection(text)

            # Проверяем наличие просьбы о помощи отдельно
            has_help = contains_help_keywords(text)

            # Определяем срочность
            urgency = detect_urgency(text)

            # Корректируем confidence на основе контекста
            if context:
                confidence = self._adjust_confidence(confidence, context)

            result = IntentResult(
                intent=intent,
                confidence=float(confidence),
                has_help_request=has_help or intent == "help_request"
            )

            processing_time = (time.time() - start_time) * 1000
            self.logger.debug(f"Intent detection took {processing_time:.2f}ms")

            return result

        except Exception as e:
            self.logger.error(f"Intent detection failed: {e}")
            raise IntentDetectionError(f"Failed to detect intent: {e}") from e

    def _rule_based_detection(self, text: str) -> tuple:
        """
        Rule-based определение намерения.

        Returns:
            tuple: (intent, confidence)
        """
        text_lower = text.lower()

        # Собираем совпадения для всех намерений
        matches = {}
        for intent_name, compiled in self.compiled_patterns.items():
            pattern = compiled['pattern']
            regex = compiled['regex']

            # Ищем все совпадения
            found = regex.findall(text_lower)
            matches_count = len(found)

            if matches_count >= pattern.min_matches:
                # Confidence зависит от количества совпадений и приоритета
                base_confidence = min(0.5 + matches_count * 0.1, 0.9)
                priority_boost = pattern.priority * 0.05
                confidence = min(base_confidence + priority_boost, 0.95)

                matches[intent_name] = confidence

        if not matches:
            return "unknown", 0.3

        # Выбираем намерение с наибольшей уверенностью
        best_intent = max(matches, key=matches.get)
        return best_intent, matches[best_intent]

    async def _ml_detection(self, text: str) -> tuple:
        """
        ML-based определение намерения (заглушка для будущего расширения).
        """
        # Здесь можно добавить модель для intent detection
        # Например, использовать тот же sentence-transformers
        return "unknown", 0.5

    def _adjust_confidence(self, confidence: float, context: Dict) -> float:
        """
        Корректирует уверенность на основе контекста.
        """
        # Если сообщение очень короткое - снижаем уверенность
        if context.get('text_length', 0) < 10:
            confidence *= 0.8

        # Если есть восклицательные знаки - повышаем для help_request
        if context.get('exclamation_count', 0) > 0:
            confidence *= 1.1

        return min(confidence, 1.0)

    def get_supported_intents(self) -> List[str]:
        """Возвращает список поддерживаемых намерений."""
        return list(self.INTENT_PATTERNS.keys())

    def add_custom_pattern(self, intent_name: str, keywords: List[str], priority: int = 1):
        """
        Добавляет пользовательский паттерн для намерения.

        Args:
            intent_name: название намерения
            keywords: список ключевых слов
            priority: приоритет
        """
        pattern = IntentPattern(
            name=intent_name,
            keywords=set(keywords),
            priority=priority
        )

        self.INTENT_PATTERNS[intent_name] = pattern
        pattern_regex = r'\b(' + '|'.join(re.escape(k) for k in keywords) + r')\b'

        self.compiled_patterns[intent_name] = {
            'pattern': pattern,
            'regex': re.compile(pattern_regex, re.IGNORECASE)
        }

        self.logger.info(f"Added custom pattern for intent: {intent_name}")