"""
Специфичные исключения для модуля суммаризации
"""

class SummarizationError(Exception):
    """Базовое исключение для всех ошибок суммаризации"""
    pass

class AlgorithmNotFoundError(SummarizationError):
    """Алгоритм не найден"""
    pass

class TextTooShortError(SummarizationError):
    """Текст слишком короткий для суммаризации"""
    pass