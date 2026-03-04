"""
STT севрис
Реализован при помощи OpenAI Whisper
Была выбрана модель Whisper,
так как она показывает низкий процент ошибок в работе с Русским языком.
"""
import whisper
import torch

import os
from pathlib import Path
from typing import Optional, Dict, Any, Union
from src.services.STT.exceptions import RecognitionError, ModelLoadError, AudioConversionError




class STTService:
    """
        Сервис для преобразования голосовых сообщений в текст.

        Особенности:
        - Поддержка русскоязычной речи
        - Работа на CPU (опционально GPU)
        - Легкая модель (tiny/base) для быстрой работы
        - Автоматическая конвертация аудио в нужный формат
    """

    # Модели Whisper
    AVAILABLE_MODELS = {
        "tiny": {"size_mb": 75, "speed": "fastest", "accuracy": "low"},
        "base": {"size_mb": 142, "speed": "fast", "accuracy": "medium"},
        "small": {"size_mb": 466, "speed": "medium", "accuracy": "good"},
        "medium": {"size_mb": 1500, "speed": "slow", "accuracy": "better"},
        "large": {"size_mb": 3000, "speed": "slowest", "accuracy": "best"},
    }

    def __init__(self,
            model_name: str = "base",
            device: Optional[str] = None,
            language: str = "ru",
            download_root: Optional[str] = None):

        '''Хотим использовать видеокарту, для работы whisper, так как на ней быстрее
            если это невозмонжно, то cpu'''
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

            # Путь для кэша моделей
            if download_root is None:
                # По умолчанию: ./services/stt/models_cache/
                self.download_root = Path(__file__).parent / "models_cache"
                self.download_root.mkdir(exist_ok=True)
            else:
                self.download_root = Path(download_root)

            # Пытаемся загрузить whisper
            try:
                print(f"Loading Whisper model '{model_name}' on {self.device}...")
                self.model = whisper.load_model(
                    model_name,
                    device=self.device,
                    download_root=str(self.download_root)
                )
                print("Model loaded successfully")
            except Exception as e:
                raise ModelLoadError(f"Failed to load Whisper model: {e}") from e