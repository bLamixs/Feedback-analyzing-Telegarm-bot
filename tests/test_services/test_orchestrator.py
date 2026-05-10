import pytest
from src.core.orchestrator import Orchestrator
from src.core.models import UserContext


@pytest.mark.asyncio
async def test_process_text(orchestrator):
    ctx = UserContext(user_id=1, chat_id=1, username="test")
    response = await orchestrator.process_text("привет", ctx, message_id=123)
    assert "ВНИМАНИЕ" not in response  # нет просьбы о помощи
    assert "Тональность" in response or "обработано" in response


@pytest.mark.asyncio
async def test_process_voice(orchestrator, mock_stt):
    # Подменяем mock_stt так, чтобы он возвращал осмысленный текст
    mock_stt.return_value = {"text": "помогите сломалось", "processing_time": 0.2}
    # orchestrator уже содержит этот mock из фикстуры
    ctx = UserContext(user_id=2, chat_id=2)
    response = await orchestrator.process_voice(b"fake_audio_data", ctx, 456, duration=3.0)
    assert "помогите" in response.lower() or "ВНИМАНИЕ" in response