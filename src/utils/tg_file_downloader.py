"""
Загрузка аудио файлов из телеграмма
"""


import os
import asyncio
import tempfile
from pathlib import Path
from typing import Union, Optional, Callable
from datetime import datetime
from aiogram import Bot
import aiohttp
import aiofiles
from aiogram.types import File

class TelegramDownloader(object):
    '''Загрузка файлов из телеграма


        С заделом на будущее загрузка будет асинхронной
        Будут осуществляться повторные попытки и обработка ошибок
        Директории для временных файлов будут создаваться автоматически'''

    def __init__(self, bot:Bot, base_dir: Union[str, Path] = "data/audio"):
        """Инициализируем загрузчика файлов
        bot - собственно, бот бля отзывов
        base_dir - директории, в которую будут сохраняться файлы. По умолчанию, это будет data/audio"""
        self.bot = bot
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def download_by_file_id(self,
                                  file_id:str,
                                  custom_filename: Optional[str] = None,
                                  progress_callback: Optional[Callable[[int, int], None]] = None,) -> Path:
        """Асинхронно скачивает файл по его file_id
        Аргументы:
            file_id - строка-айди файла
            custom_filename - пользовательское имя файла, если его нет, то сгенерируем
            progress_callback - будем также отслеживать прогресс скачивания файла, чтобы польователь не ждал

        Возвращает:
            Функция возвращает путь к скачанному файлц
        Ошибки:
            FileNotFoundError - если не найден файл в Телеграмме
            Exception - исключения при ошибках загрузки """

        try:
            file_info = await self.bot.get_file(file_id)

            if custom_filename:
                filename = custom_filename
            else:
                filename = self._generate_filename(file_info)

            file_path = self.base_dir / filename

            await self.download_file(file_path=file_info.file_path,
                                     destination=file_path,
                                     progress_callback=progress_callback)
            return file_path
        except Exception as e:
            raise Exception(f"Failed to download file {file_id}: {e}")

    async def download_voice(self,
                             voice,
                             user_id: int,
                             message_id: int,
                             progress_callback: Optional[Callable[[int, int], None]] = None) -> Path:
        """ Отдельный метод для скачивания голосовых сообщений
        АРгументы:
            voice: объект Voice из Telegram
            user_id: ID пользователя (для имени файла)
            message_id: ID сообщения (для имени файла)
            progress_callback: функция отслеживания прогресса

        Возвращает:
            путь к скачанному файлу
            """
        time_stamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"voice_{user_id}_{message_id}_{time_stamp}.ogg"

        return await self.download_by_file_id(file_id=voice.file_id,
                                              custom_filename=filename,
                                              progress_callback=progress_callback)
    async def download_audio(self, audio,
                             user_id: int, message_id: int,
                             progress_callback: Optional[Callable[[int, int], None]] = None) -> Path:
        """
        Функция для загрузки аудиофайлов

        :param audio: объект Audio из тг
        :param user_id: айдишник юзера для имени файла
        :param message_id: айдшник сообщения
        :param progress_callback: функция для отслеживания прогресса загрузки

        :return: путь к скаченному файлу
        """

        if audio.mime_type:
            ext = audio.mime_type.split("/")[-1]
        else:
            ext = 'mp3'

        time_stamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"audio_{user_id}_{message_id}_{time_stamp}.{ext}"

        return await self.download_by_file_id(file_id=audio.file_id,
                                              custom_filename=filename,
                                              progress_callback=progress_callback)

    async def _download_file(
            self,
            file_path: str,
            destination: Path,
            progress_callback: Optional[Callable[[int, int], None]] = None,
            max_retries: int = 3
    ) -> None:
        """
        Внутренний метод для скачивания файла.

        Args:
            file_path: путь к файлу на серверах Telegram
            destination: локальный путь для сохранения
            progress_callback: функция отслеживания прогресса
            max_retries: количество попыток при ошибке
        """
        # Формируем URL для скачивания
        url = f"https://api.telegram.org/file/bot{self.bot.token}/{file_path}"

        # Создаем директорию назначения
        destination.parent.mkdir(parents=True, exist_ok=True)

        for attempt in range(max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status != 200:
                            raise Exception(f"HTTP {response.status}: {response.reason}")

                        # Получаем размер файла
                        total_size = int(response.headers.get('content-length', 0))
                        downloaded = 0

                        # Скачиваем файл
                        async with aiofiles.open(destination, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                await f.write(chunk)
                                downloaded += len(chunk)

                                # Вызываем callback прогресса
                                if progress_callback and total_size > 0:
                                    progress_callback(downloaded, total_size)

                        # Успешно скачали
                        return

            except Exception as e:
                if attempt == max_retries - 1:
                    raise Exception(f"Failed after {max_retries} attempts: {e}")
                await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff

    def _generate_filename(self, file_info: File) -> str:
        """
        Генерирует уникальное имя файла.

        Args:
            file_info: информация о файле из Telegram

        Returns:
            str: сгенерированное имя файла
        """
        # Определяем расширение из file_path
        if file_info.file_path and '.' in file_info.file_path:
            ext = file_info.file_path.split('.')[-1]
        else:
            ext = 'bin'

        # Генерируем уникальное имя
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = os.urandom(4).hex()

        return f"file_{timestamp}_{unique_id}.{ext}"

    async def cleanup_old_files(self, hours: int = 24) -> int:
        """
        Удаляет файлы старше указанного количества часов.

        Args:
            hours: возраст файлов в часах

        Returns:
            int: количество удаленных файлов
        """
        import time

        deleted = 0
        current_time = time.time()

        for file_path in self.base_dir.glob("*"):
            if file_path.is_file():
                # Получаем время модификации
                mtime = file_path.stat().st_mtime
                age_hours = (current_time - mtime) / 3600

                if age_hours > hours:
                    try:
                        file_path.unlink()
                        deleted += 1
                    except Exception as e:
                        print(f"Error deleting {file_path}: {e}")

        return deleted


# Создаем экземпляр загрузчика (синглтон)
_downloader_instance = None


def get_downloader(bot: Bot) -> TelegramDownloader:
    """
    Возвращает экземпляр загрузчика (синглтон).

    Args:
        bot: экземпляр бота

    Returns:
        TelegramDownloader: экземпляр загрузчика
    """
    global _downloader_instance
    if _downloader_instance is None:
        _downloader_instance = TelegramDownloader(bot)
    return _downloader_instance