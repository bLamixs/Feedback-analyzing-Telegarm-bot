"""
STT севрис
Реализован при помощи OpenAI Whisper
Была выбрана модель Whisper,
так как она показывает низкий процент ошибок в работе с Русским языком.
"""
import whisper
import torch

import os
import librosa
from pathlib import Path
from typing import Optional, Dict, Any, Union
from src.services.STT.exceptions import RecognitionError, ModelLoadError, AudioConversionError
from src.services.STT.utils import convert_to_wav, validate_audio, cleanup_temp_files


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

        self.model_name = model_name
        self.language = language

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

    async def transcribe(self,
                         audio_input: Union[str,bytes, Path],
                         **kwargs) -> Dict[str, Any]:
        """Реализуем метод по рспознавнию речи

            ARgs:
                audio_path: путь к аудиофайлу или его байтовое представление (все это будет получать из тг)
                **kwargs: список различных дополнитльеных параметров, которые могут понавдобитьься модели whisper для рпботы

            Returns:
                словарь с результатми распознования записис:
                {text : текст аудио
                language: язык
                segments: сегменты с таймкоадми
                duration: длительность аудио файла
                processing_time: время работы (обработки) аудио файла в секундах (хочу использовать для дальнейшего получения статистики)
            Возможные ошибки:
                AudioConvertationError - не удаось ковертировать в текст полученный аудио файл
                RecognitionError - не удалось распознавание """
        import time
        import tempfile

        temp_files = []

        try:
            start_time = time.time()

            if isinstance(audio_input, bytes):
                with tempfile.NamedTemporaryFile(suffix='.ogg', delete = False ) as f:
                    f.write(audio_input)
                    input_path = f.name
                    temp_files.append(input_path)
            elif isinstance(audio_input, (str,Path)):
                input_path = str(audio_input)
            else:
                raise ValueError(f"Unsupported audio input type: {type(audio_input)}")

            wav_path = await convert_to_wav(input_path)
            temp_files.append(wav_path)


            is_valid, message = validate_audio(wav_path)
            if not is_valid:
                raise RecognitionError(f"Invalid audio: {message}")

            result = self.model.transcribe(wav_path,
                                           language = self.language,
                                           fp16=(self.device == "cuda"),
                                           **kwargs
                                           )
            processing_time = time.time() - start_time
            result['processing_time'] = processing_time
            result['duration'] = self._get_audio_duration(wav_path)

            return result

        except Exception as e:
            raise RecognitionError(f"Failed to transcribe audio: {e}") from e

        finally:
            await cleanup_temp_files(*temp_files)

    async def transcribe_simple(self, audio_input: Union[str, bytes]) -> str:
        """
        Упрощенный метод, возвращает только текст.

        Args:
            audio_input: путь к аудиофайлу или бинарные данные

        Returns:
            распознанный текст
        """
        result = await self.transcribe(audio_input)
        return result.get("text", "")

    def _get_audio_duration(self, audio_path: str) -> float:
        """
        Получает длительность аудиофайла.
        """
        try:
            duration = librosa.get_duration(filename=audio_path)
            return duration
        except Exception as e:
            raise RecognitionError(f"Failed to get audio duration: {e}") from e
            return 0.0

