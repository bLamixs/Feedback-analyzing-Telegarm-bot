"""
Обработчик голосовых сообщений.
Скачивает аудио, передаёт в оркестратор.
"""

import os
import tempfile
from aiogram import Router, types
from aiogram.fsm.context import FSMContext

from core import orchestrator, UserContext
from utils import tg_file_downloader
from config.settings import settings

router = Router(name="voices")
orchestrator = Orchestrator(config=settings.ORCHESTRATOR_CONFIG)


@router.message(lambda message: message.voice is not None)
async def handle_voice(message: types.Message, state: FSMContext):
    """Обработка голосовых сообщений."""
    try:
        # Отправляем уведомление
        status_msg = await message.answer("🎤 Получил голосовое сообщение. Начинаю обработку...")

        # Скачиваем аудио
        downloader = TelegramDownloader(bot=message.bot)
        file_path = await downloader.download_voice(
            voice=message.voice,
            user_id=message.from_user.id,
            message_id=message.message_id
        )

        await status_msg.edit_text("📝 Распознаю речь и анализирую...")

        # Контекст пользователя
        user_ctx = UserContext(
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            chat_id=message.chat.id
        )

        # Читаем файл в байты
        with open(file_path, 'rb') as f:
            audio_bytes = f.read()

        # Обрабатываем через оркестратор
        response = await orchestrator.process_voice(
            audio_bytes=audio_bytes,
            user_context=user_ctx,
            message_id=message.message_id,
            duration=message.voice.duration
        )

        # Удаляем временный файл
        os.unlink(file_path)
        await status_msg.delete()
        await message.answer(response, parse_mode="Markdown")

    except Exception as e:
        await message.answer(f"❌ Ошибка при обработке голосового: {str(e)}")