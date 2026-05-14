"""
Обработчик голосовых сообщений.
Скачивает аудио, передаёт в оркестратор.
"""

import os
from aiogram import Router, types
from aiogram.fsm.context import FSMContext

from src.core import Orchestrator  # ← ИСПРАВЛЕНО: импортируем класс
from src.core.models import UserContext
from src.utils.tg_file_downloader import TelegramDownloader
from src.config import settings

router = Router(name="voices")

# ПРАВИЛЬНОЕ создание оркестратора
_orchestrator = Orchestrator(config=settings.orchestrator_config)  # ← строчные буквы!


def set_orchestrator(orch):
    """Устанавливает оркестратор (для тестов)."""
    global _orchestrator
    _orchestrator = orch


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
        response = await _orchestrator.process_voice(  # ← _orchestrator с нижним подчёркиванием
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