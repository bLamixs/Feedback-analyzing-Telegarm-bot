"""
Обработчик текстовых сообщений.
"""

from aiogram import Router, types
from aiogram.fsm.context import FSMContext

from src.config import settings
from src.core import Orchestrator, UserContext

router = Router(name="texts")

_orchestrator = Orchestrator(config=settings.orchestrator_config)  # ← строчные буквы!


def set_orchestrator(orch):
    """Устанавливает оркестратор (для тестов)."""
    global _orchestrator
    _orchestrator = orch


@router.message(lambda message: message.text and not message.text.startswith('/'))
async def handle_text(message: types.Message, state: FSMContext):
    """Обработка текстовых сообщений."""
    if _orchestrator is None:
        await message.answer("❌ Оркестратор не инициализирован")
        return

    # Создаём контекст пользователя
    user_ctx = UserContext(
        user_id=message.from_user.id,
        chat_id=message.chat.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )

    try:
        # Отправляем статус
        status_msg = await message.answer("🔍 Анализирую сообщение...")

        # Обрабатываем через оркестратор
        response = await _orchestrator.process_text(
            text=message.text,
            user_context=user_ctx,
            message_id=message.message_id
        )

        # Удаляем статусное сообщение
        await status_msg.delete()

        # Отправляем результат
        await message.answer(response, parse_mode="Markdown")

    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")