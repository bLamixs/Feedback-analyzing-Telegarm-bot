"""
    Настройка алгоритмов суммаризации
"""

from typing import Dict, Type
from dataclasses import dataclass

from sumy.summarizers import lsa, luhn, edmundson, text_rank

from src.services.Summarisation_service.exceptions import AlgorithmNotFoundError


@dataclass
class AlgorithmConfig:
    """Конфигурация алгоритма суммаризации"""

    name: str
    description: str
    summarizer_class: Type
    default_sentences: int = 3
    language: str = 'russian'
    pros: str = ""
    cons: str = ""

# Доступные алгоритмы
ALGORITHMS = {
    "lsa": AlgorithmConfig(
        name="LSA",
        description="Latent Semantic Analysis - анализ скрытых семантических связей",
        summarizer_class=lsa.LsaSummarizer,
        default_sentences=3,
        pros="Лучший баланс скорости и качества, хорошо работает на русском",
        cons="Может выделять не самые важные предложения"
    ),
    "textrank": AlgorithmConfig(
        name="TextRank",
        description="Графовый алгоритм на основе PageRank",
        summarizer_class=text_rank.TextRankSummarizer,
        default_sentences=3,
        pros="Учитывает связи между предложениями",
        cons="Медленнее LSA на длинных текстах"
    ),
    "luhn": AlgorithmConfig(
        name="Luhn",
        description="Классический частотный анализ",
        summarizer_class=luhn.LuhnSummarizer,
        default_sentences=3,
        pros="Очень быстрый, простой",
        cons="Менее точен, игнорирует контекст"
    ),
    "edmundson": AlgorithmConfig(
        name="Edmundson",
        description="Учитывает позицию предложения и ключевые слова",
        summarizer_class=edmundson.EdmundsonSummarizer,
        default_sentences=3,
        pros="Хорош для структурированных текстов",
        cons="Требует настройки весов"
    ),
}

def get_algorithm(name: str):
    """
    Возвращаем класс алгоритма по имени
    :param name: имя алгоритма
    :return: класс суммаризатора
    :raises: AlgorithmNotFoundError - если алгоритм не найден
    """
    if name not in ALGORITHMS:
        raise AlgorithmNotFoundError(f"Algorithm '{name}' not found. Available algorithms: {list(ALGORITHMS.keys())}")
    return ALGORITHMS[name].summarizer_class

def list_algorithms() -> Dict:
    """
    Возвращает информацию обо всех досутпных алгоритмах
    """
    return {name: {
        "name": config.name,
        "description": config.description,
        "pros": config.pros,
        "cons": config.cons
    } for name, config in ALGORITHMS.items()}
