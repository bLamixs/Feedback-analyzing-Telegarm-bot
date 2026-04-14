"""
Утилиты модуля суммаризации
"""

import re
from typing import List, Tuple

def split_into_sentences(text: str) -> List[str]:
    """
    Разбивает текст на предложения

    :param text: исходный полученнный текст от пользователя
    :return: список предложений
    """
    sentences = re.split(r'[.!?]+', text)
    return [s.strip() for s in sentences if s.strip()]

def estimate_optimal_sentences_count(text: str, min_sentences:int = 1, max_sentences:int = 5) -> int:
    """
    Функция оценивает оптимальное количество предложений для суммаризации
    :param text: исходный текст
    :param min_sentences: минимально возможное количество предложений
    :param max_sentences: максимально возможное количество предложений
    :return: оптимальное (рекомендуемое) количество предложений
    """

    sentences = split_into_sentences(text)
    total_sentences = len(sentences)

    if total_sentences <= 3:
        return max(1, total_sentences - 1)

    # Для длинных текстов будем ограничиваться одной пятой от количества приложений
    recommended_sentences = max(min_sentences, int(total_sentences * 0.2))

    #Если текст очень большой, то все равно делаем 5 предложений
    return min(recommended_sentences, max_sentences)

def get_text_stats(text: str) -> dict:
    """
    Возвращает статистику тектса
    :param text: исходный текст
    :return: словарь со статистикой
    """

    sentences = split_into_sentences(text)
    words = text.split()

    return {
        "char_count": len(text),
        "word_count": len(words),
        "sentence_count": len(sentences),
        "avg_word_length": sum(len(w) for w in words) / len(words) if words else 0,
        "avg_sentence_length": len(words) / len(sentences) if sentences else 0
    }

