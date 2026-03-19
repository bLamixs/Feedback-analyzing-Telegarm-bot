"""
NLP анализ текста для "Кибер-секретаря".
Включает анализ тональности, классификацию темы и определение намерения.
"""

from .NLP_service import NLPAnalysisService
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
    'NLPAnalysisService',
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