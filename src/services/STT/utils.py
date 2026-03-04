"""
Утилиты для STT сервиса
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple

import librosa
import soundfile as sf


async def convert_to_wav(input_path: str, output_path: Optional[str] = None) -> str:
    """
    Конвертирует аудиофайл в формат WAV (16kHz, mono) с помощью ffmpeg.

    Args:
        input_path: путь к исходному аудиофайлу (сыылку получать будем через tg, пока не смотрел как)
        output_path: путь для сохранения результата (если None, создается временный файл)

    Returns:
        путь к конвертированному WAV файлу

    Raises:
        AudioConversionError: если конвертация не удалась
    """
    if not output_path:
        # Создаем временный файл с расширением .wav
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            output_path = tmp.name

    # Команда ffmpeg для конвертации в нужный формат
    # Whisper ожидает: 16kHz, mono, WAV
    cmd = [
        'ffmpeg',
        '-i', input_path,  # входной файл
        '-ar', '16000',  # частота дискретизации 16kHz
        '-ac', '1',  # mono (1 канал)
        '-c:a', 'pcm_s16le',  # кодек PCM 16-bit
        '-y',  # перезаписывать выходной файл
        output_path
    ]

    try:
        # Запускаем ffmpeg и ждем завершения
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        raise AudioConversionError(
            f"FFmpeg error: {e.stderr}"
        ) from e
    except FileNotFoundError as e:
        raise AudioConversionError(
            "FFmpeg not found. Please install ffmpeg."
        ) from e

    return output_path


def validate_audio(file_path: str, min_duration: float = 0.5) -> Tuple[bool, str]:
    """
    Проверяет качество аудиофайла.

    Args:
        file_path: путь к аудиофайлу
        min_duration: минимальная допустимая длительность в секундах

    Returns:
        (is_valid, message) - флаг валидности и сообщение
    """
    try:
        # Загружаем аудио для анализа
        y, sr = librosa.load(file_path, sr=None)

        # Проверка длительности
        duration = librosa.get_duration(y=y, sr=sr)
        if duration < min_duration:
            return False, f"Audio too short: {duration:.2f}s (min: {min_duration}s)"

        # Проверка энергии (не тихий ли файл)
        energy = np.mean(np.abs(y))
        if energy < 0.001:
            return False, "Audio too quiet or silent"

        return True, f"Valid audio: {duration:.2f}s, energy: {energy:.4f}"

    except Exception as e:
        return False, f"Audio validation failed: {str(e)}"


def normalize_audio(file_path: str) -> str:
    """
    Нормализует громкость аудио.

    Args:
        file_path: путь к аудиофайлу

    Returns:
        путь к нормализованному файлу
    """
    y, sr = librosa.load(file_path, sr=16000)

    # Нормализация громкости (peak normalization)
    y_normalized = y / np.max(np.abs(y))

    # Сохраняем во временный файл
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        sf.write(tmp.name, y_normalized, sr)
        return tmp.name


async def cleanup_temp_files(*file_paths):
    """
    Удаляет временные файлы.

    Args:
        *file_paths: пути к файлам для удаления
    """
    for path in file_paths:
        try:
            if path and os.path.exists(path):
                os.unlink(path)
        except Exception as e:
            # Логируем, но не прерываем выполнение
            print(f"Failed to delete {path}: {e}")