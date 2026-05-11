import pytest
from aiogram.types import Message, Voice, User, Chat
from src.bot.handlers import text_handler, audio_handler


@pytest.fixture
def mock_message():
    msg = Message(
        message_id=1,
        date=None,
        chat=Chat(id=123, type="private"),
        from_user=User(id=123, is_bot=False, first_name="Test"),
        text="/start"
    )
    return msg


@pytest.mark.asyncio
async def test_text_handler(mock_message, orchestrator):
    # Передаём оркестратор в обработчик через глобальный сеттер
    text_handler.set_orchestrator(orchestrator)
    # Мокаем метод answer
    mock_message.answer = AsyncMock()
    await text_handler.handle_text(mock_message)
    mock_message.answer.assert_called_once()


@pytest.mark.asyncio
async def test_voice_handler():
    # Создаём объект Voice
    voice = Voice(file_id="test", duration=2.5)
    msg = Message(
        message_id=2, date=None, chat=Chat(id=123, type="private"),
        from_user=User(id=123, is_bot=False, first_name="Test"),
        voice=voice
    )
    msg.answer = AsyncMock()
    msg.bot = AsyncMock()
    msg.bot.get_file = AsyncMock(return_value=type('File', (), {'file_path': 'path'}))
    with patch("utils.telegram_downloader.TelegramDownloader.download_voice", return_value="/tmp/fake.ogg"):
        audio_handler.set_orchestrator(orchestrator)
        await audio_handler.handle_voice(msg, None)
        msg.answer.assert_called()