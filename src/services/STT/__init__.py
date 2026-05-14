"""
Speech-to-Text модуль для преобразования голосовых сообщений в текст.
Использует OpenAI Whisper для распознавания русской речи.
"""

from .STTservice import STTService
from .exceptions import STTError, AudioConversionError, RecognitionError

__all__ = [
    'STTService',
    'STTError',
    'AudioConversionError',
    'RecognitionError',
]