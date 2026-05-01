"""
Обработчики системных команд: /start, /help, /info.
"""

from aiogram import Router, types
from aiogram.filters import Command

router = Router(name="commands")


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """Приветствие нового пользователя."""
    user = message.from_user
    welcome_text = (
        f"👋 Привет, {user.first_name}!\n\n"
        "Я — **Кибер-секретарь** 🤖\n"
        "Я умею анализировать текстовые и голосовые сообщения:\n"
        "• Определять тональность (позитив/негатив)\n"
        "• Выделять тему обращения\n"
        "• Понимать, есть ли просьба о помощи\n"
        "• Составлять краткое содержание\n\n"
        "Просто отправь мне текст или голосовое сообщение — и я отвечу!"
    )
    await message.answer(welcome_text, parse_mode="Markdown")


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    """Справка по использованию бота."""
    help_text = (
        "📖 **Справка по использованию**\n\n"
        "✅ **Что я умею:**\n"
        "• Анализировать текстовые сообщения\n"
        "• Распознавать речь из голосовых сообщений\n"
        "• Определять настроение и тему\n"
        "• Выделять суть сообщения\n\n"
        "📌 **Команды:**\n"
        "/start — приветствие\n"
        "/help — эта справка\n"
        "/info — информация о боте\n"
        "/stats — (в разработке) ваша статистика\n\n"
        "💡 **Совет:** говорите чётко, чтобы распознавание было точнее."
    )
    await message.answer(help_text, parse_mode="Markdown")


@router.message(Command("info"))
async def cmd_info(message: types.Message):
    """Информация о версии и авторе."""
    info_text = (
        "🤖 **Кибер-секретарь v1.0**\n\n"
        "Разработан в рамках дипломного проекта.\n"
        "Технологии:\n"
        "• Whisper (распознавание речи)\n"
        "• ruBERT (анализ тональности)\n"
        "• Sentence‑Transformers (классификация темы)\n"
        "• Sumy (суммаризация)\n\n"
        "© 2025, Агеев Дмитрий"
    )
    await message.answer(info_text, parse_mode="Markdown")