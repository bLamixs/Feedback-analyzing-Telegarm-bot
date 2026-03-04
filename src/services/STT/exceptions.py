"""
Исключения для STT модуля
"""

class STTError(Exception):
    """Базовое исключение для всех ошибок STT модуля"""
    pass

class AudioConversionError(STTError):
    """Ошибка при конвертации аудиофайла"""
    pass

class RecognitionError(STTError):
    """Ошибка при распознавании речи"""
    pass

class ModelLoadError(STTError):
    """Ошибка при загрузке модели Whisper"""
    pass