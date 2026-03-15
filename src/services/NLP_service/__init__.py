"""
NLP анализ текста для "Кибер-секретаря".
Включает анализ тональности, классификацию темы и определение намерения.
"""

from .services import NLP_service
from .sentiment import SentimentAnalyzer
from .topic import TopicClassifier
from .intent import IntentDetector
from .models import AnalysisResult, SentimentResult, TopicResult, IntentResult
from .exceptions import (
    NLPError,
    SentimentAnalysisError,
    TopicClassificationError,
    IntentDetectionError,
    ModelLoadError
)

__all__ = [
    'NLP_service',
    'SentimentAnalyzer',
    'TopicClassifier',
    'IntentDetector',
    'AnalysisResult',
    'SentimentResult',
    'TopicResult',
    'IntentResult',
    'NLPError',
    'SentimentAnalysisError',
    'TopicClassificationError',
    'IntentDetectionError',
    'ModelLoadError'
]