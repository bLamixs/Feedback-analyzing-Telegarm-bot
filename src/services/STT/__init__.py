"""
Speech-to-Text модуль для преобразования голосовых сообщений в текст.
Использует OpenAI Whisper для распознавания русской речи.
"""

from src.services.STT import STTservice
from src.services.STT.exceptions import STTError, AudioConversionError, RecognitionError

__all__ = ['STTservice',
           'STTError',
           'AudioConversionError',
           'RecognitionError']