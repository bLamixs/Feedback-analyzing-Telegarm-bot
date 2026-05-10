import pytest
from services.stt import STTService


@pytest.mark.asyncio
async def test_transcribe_simple():
    stt = STTService(model_name="tiny", language="ru")
    # Создаём временный аудиофайл (например, тишину) - упрощённо
    # Для реального теста нужно создать валидный wav, но можно мокать
    with pytest.raises(Exception):  # ожидаем ошибку, т.к. файла нет
        await stt.transcribe_simple("nonexistent.ogg")


# Мокируем методы, чтобы не скачивать реальные аудио
@pytest.mark.asyncio
async def test_transcribe_with_mock():
    with patch("services.stt.service.convert_to_wav", return_value="fake.wav"), \
         patch("services.stt.service.validate_audio", return_value=(True, "ok")), \
         patch("services.stt.service.cleanup_temp_files", new_callable=AsyncMock):
        stt = STTService()
        # Мокаем внутренний whisper.transcribe
        stt.model.transcribe = lambda path, **kw: {"text": "тест"}
        result = await stt.transcribe_simple("dummy.ogg")
        assert result == "тест"