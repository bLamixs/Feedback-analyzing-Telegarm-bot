"""
Загрузчик файлов из Telegram.
"""

import os
import tempfile
from pathlib import Path
from typing import Optional

import aiofiles
import aiohttp
from aiogram import Bot


class TelegramDownloader:
    def __init__(self, bot: Bot, base_dir: str = "data/audio"):
        self.bot = bot
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def download_voice(self, voice, user_id: int, message_id: int) -> Path:
        """Скачивает голосовое сообщение и возвращает путь к файлу."""
        file_info = await self.bot.get_file(voice.file_id)
        # Генерируем имя
        filename = f"voice_{user_id}_{message_id}.ogg"
        file_path = self.base_dir / filename

        # Скачиваем
        url = f"https://api.telegram.org/file/bot{self.bot.token}/{file_info.file_path}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    async with aiofiles.open(file_path, "wb") as f:
                        await f.write(await resp.read())
                else:
                    raise Exception(f"Failed to download: {resp.status}")
        return file_path