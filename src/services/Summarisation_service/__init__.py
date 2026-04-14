"""
Модуль экстрактивной суммаризации текста.
Основан на библиотеке Sumy.
"""

from .service import SummarizationService, SummarizationResult
from .exceptions import (
    SummarizationError,
    AlgorithmNotFoundError,
    TextTooShortError
)
from .algorithms import list_algorithms

__all__ = [
    'SummarizationService',
    'SummarizationResult',
    'SummarizationError',
    'AlgorithmNotFoundError',
    'TextTooShortError',
    'list_algorithms'
]