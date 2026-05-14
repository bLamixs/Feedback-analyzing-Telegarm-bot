"""
Обработчик текстовых сообщений.
Передаёт текст в оркестратор и возвращает результат.
"""

from aiogram import Router, types
from aiogram.fsm.context import FSMContext

from src.core import orchestrator
from src.core.models import UserContext
from src.config import settings

router = Router(name="texts")

# Инициализируем оркестратор (можно сделать синглтон)
orchestrator = orchestrator(config=settings.ORCHESTRATOR_CONFIG)


@router.message(lambda message: message.text and not message.text.startswith('/'))
async def handle_text(message: types.Message, state: FSMContext):
    """
    Обработка любого текстового сообщения (не команды).
    """
    try:
        # Сообщаем пользователю, что начали обработку
        status_msg = await message.answer("🔍 Анализирую сообщение...")

        # Формируем контекст пользователя
        user_ctx = UserContext(
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            chat_id=message.chat.id
        )

        # Вызываем оркестратор
        response = await orchestrator.process_text(
            text=message.text,
            user_context=user_ctx,
            message_id=message.message_id
        )

        # Удаляем статусное сообщение
        await status_msg.delete()

        # Отправляем результат
        await message.answer(response, parse_mode="Markdown")

    except Exception as e:
        await message.answer(f"❌ Ошибка при обработке: {str(e)}")