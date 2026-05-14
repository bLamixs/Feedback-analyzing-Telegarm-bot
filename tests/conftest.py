# tests/conftest.py

from dotenv import load_dotenv
from pathlib import Path

# Находим корень проекта (папка, где лежит main.py и .env)
BASE_DIR = Path(__file__).parent.parent  # поднимаемся на уровень выше tests/
env_path = BASE_DIR / ".env"

# Загружаем .env с явным указанием пути
load_dotenv(dotenv_path=env_path)
import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from src.config import settings
from src.core.orchestrator import Orchestrator
from src.services.STT import STTservice
from src.services.NLP_service import NLP_service
from src.services.Summarisation_service import service
from src.services.storage import storage_service


@pytest.fixture(autouse=True)
def mock_settings_env(monkeypatch):
    """Подменяем переменные окружения для тестов."""
    monkeypatch.setattr(settings, "BOT_TOKEN", "test_token")
    monkeypatch.setattr(settings, "DEBUG", False)
    monkeypatch.setattr(settings, "STT_MODEL", "tiny")  # лёгкая модель для тестов


@pytest.fixture
def mock_stt():
    with patch("services.stt.STTService.transcribe") as mock:
        mock.return_value = {"text": "привет мир", "processing_time": 0.5}
        yield mock


@pytest.fixture
def mock_nlp():
    mock = AsyncMock()
    mock.analyze.return_value = MockAnalysisResult()
    yield mock


@pytest.fixture
def mock_summarizer():
    mock = AsyncMock()
    mock.summarize_simple.return_value = "краткое содержание"
    yield mock


@pytest.fixture
def mock_storage():
    mock = AsyncMock()
    mock.save_message.return_value = None
    mock.get_user_history.return_value = []
    yield mock


@pytest.fixture
def orchestrator(mock_stt, mock_nlp, mock_summarizer, mock_storage):
    orch = Orchestrator(
        stt_service=mock_stt,
        nlp_service=mock_nlp,
        summarization_service=mock_summarizer,
        storage_service=mock_storage,
        config={}
    )
    return orch


# Вспомогательный класс для имитации результата NLP
class MockAnalysisResult:
    sentiment = type('Sentiment', (), {'label': 'positive', 'score': 0.95})
    topic = type('Topic', (), {'topic': 'feedback', 'score': 0.9})
    intent = type('Intent', (), {'intent': 'feedback', 'has_help_request': False})