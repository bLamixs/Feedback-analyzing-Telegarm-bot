"""
Вспомогательные функции для NLP модуля.
"""

import re
import string
from typing import List, Optional


def clean_text(text: str, remove_punctuation: bool = True) -> str:
    """
    Очищает текст от лишних символов.

    Args:
        text: исходный текст
        remove_punctuation: удалять ли пунктуацию

    Returns:
        очищенный текст
    """
    if not text:
        return ""

    # Приводим к нижнему регистру
    text = text.lower()

    # Удаляем лишние пробелы
    text = re.sub(r'\s+', ' ', text)

    # Удаляем пунктуацию если нужно
    if remove_punctuation:
        text = text.translate(str.maketrans('', '', string.punctuation))

    return text.strip()


def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """
    Извлекает ключевые слова из текста.

    Args:
        text: исходный текст
        min_length: минимальная длина слова

    Returns:
        список ключевых слов
    """
    words = re.findall(r'\b\w+\b', text.lower())
    return [w for w in words if len(w) >= min_length]


def contains_help_keywords(text: str) -> bool:
    """
    Проверяет, содержит ли текст ключевые слова просьбы о помощи.

    Args:
        text: исходный текст

    Returns:
        True если есть ключевые слова
    """
    help_keywords = [
        'помоги', 'пожалуйста', 'срочно', 'не работает',
        'сломалось', 'ошибка', 'проблема', 'не могу',
        'help', 'please', 'error', 'broken', 'issue'
    ]

    text_lower = text.lower()
    for keyword in help_keywords:
        if keyword in text_lower:
            return True
    return False


def detect_urgency(text: str) -> float:
    """
    Определяет уровень срочности сообщения (0-1).

    Args:
        text: исходный текст

    Returns:
        уровень срочности
    """
    urgency_keywords = [
        'срочно', 'быстро', 'немедленно', 'скорее',
        'urgent', 'asap', 'immediately'
    ]

    text_lower = text.lower()
    urgency_score = 0.0

    for keyword in urgency_keywords:
        if keyword in text_lower:
            urgency_score += 0.3

    # Восклицательные знаки тоже признак срочности
    exclamation_count = text.count('!')
    urgency_score += min(exclamation_count * 0.1, 0.4)

    return min(urgency_score, 1.0)