import pytest
from services.storage import StorageService
from core.models import ProcessedMessage, UserContext


@pytest.mark.asyncio
async def test_save_and_get_message():
    # Используем SQLite in-memory для тестов
    storage = StorageService()
    # Переопределяем URL БД для теста (можно через monkeypatch)
    import services.storage.database
    services.storage.database.settings.DATABASE_URL = "sqlite+aiosqlite:///:memory:"
    await storage.initialize()

    user_ctx = UserContext(user_id=123, chat_id=123, username="tester")
    processed = ProcessedMessage(
        message_id=1,
        user_id=123,
        message_type="text",
        original_text="hello",
        recognized_text=None,
        sentiment="positive",
        sentiment_score=0.9,
        topic="feedback",
        topic_score=0.8,
        intent="greeting",
        has_help_request=False,
        summary="summary",
        processing_time_ms=100
    )
    await storage.save_message(processed, user_ctx)

    history = await storage.get_user_history(123, limit=1)
    assert len(history) == 1
    assert history[0]["analysis"]["sentiment"] == "positive"
    await storage.close()