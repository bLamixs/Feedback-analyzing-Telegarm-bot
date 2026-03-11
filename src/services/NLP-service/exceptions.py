"""
Специфичные исключения для NLP модуля.
"""

class NLPError(Exception):
    """Базовое исключение для всех ошибок NLP модуля"""
    pass

class SentimentAnalysisError(NLPError):
    """Ошибка при анализе тональности"""
    pass

class TopicClassificationError(NLPError):
    """Ошибка при классификации темы"""
    pass

class IntentDetectionError(NLPError):
    """Ошибка при определении намерения"""
    pass

class ModelLoadError(NLPError):
    """Ошибка при загрузке модели"""
    pass