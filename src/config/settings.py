"""
Конфигурация приложения.
Загружает переменные из .env (в корне проекта).
"""

import os
from pathlib import Path
from typing import Optional, List

from dotenv import load_dotenv

# ============================================
# ЗАГРУЗКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ ИЗ .env
# ============================================

# Находим корень проекта (папка, где лежит main.py и .env)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_path = BASE_DIR / ".env"

# Загружаем .env в переменные окружения
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"✅ Загружен .env из {env_path}")
else:
    print(f"⚠️ Файл .env не найден по пути {env_path}")


class Settings:
    """
    Настройки приложения.
    Все переменные читаются из os.environ (куда загружен .env).
    """

    # ============================================
    # Telegram Bot Configuration
    # ============================================
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")

    # ============================================
    # Database Configuration
    # ============================================
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/cyber_secretary.db")
    DB_ECHO: bool = os.getenv("DB_ECHO", "false").lower() == "true"
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "10"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    # ============================================
    # Admin Configuration (опционально)
    # ============================================
    ADMIN_ID: int = int(os.getenv("ADMIN_ID", "0"))

    # ============================================
    # Debug & Logging
    # ============================================
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # ============================================
    # STT (Whisper) Configuration
    # ============================================
    STT_MODEL: str = os.getenv("STT_MODEL", "base")
    STT_LANGUAGE: str = os.getenv("STT_LANGUAGE", "ru")
    STT_DEVICE: Optional[str] = os.getenv("STT_DEVICE", None)

    # ============================================
    # NLP Configuration
    # ============================================
    USE_GPU: bool = os.getenv("USE_GPU", "true").lower() == "true"
    NLP_TOPICS: str = os.getenv(
        "NLP_TOPICS",
        "техническая поддержка,жалоба на сервис,предложение по улучшению,просто отзыв,спам"
    )

    @property
    def topics_list(self) -> List[str]:
        """Возвращает список тем как список строк."""
        return [t.strip() for t in self.NLP_TOPICS.split(",") if t.strip()]

    # ============================================
    # Summarization Configuration
    # ============================================
    SUMMARIZER_ALGORITHM: str = os.getenv("SUMMARIZER_ALGORITHM", "lsa")
    SUMMARIZER_LANGUAGE: str = os.getenv("SUMMARIZER_LANGUAGE", "russian")
    MAX_SUMMARY_SENTENCES: int = int(os.getenv("MAX_SUMMARY_SENTENCES", "3"))

    # ============================================
    # File Storage Configuration
    # ============================================
    AUDIO_TEMP_DIR: str = os.getenv("AUDIO_TEMP_DIR", "data/audio")
    KEEP_AUDIO_FILES: bool = os.getenv("KEEP_AUDIO_FILES", "false").lower() == "true"
    MAX_AUDIO_AGE_HOURS: int = int(os.getenv("MAX_AUDIO_AGE_HOURS", "24"))

    @property
    def audio_dir_abs(self) -> Path:
        """Абсолютный путь к папке аудио."""
        return BASE_DIR / self.AUDIO_TEMP_DIR

    # ============================================
    # Performance Configuration
    # ============================================
    MAX_CONCURRENT_REQUESTS: int = int(os.getenv("MAX_CONCURRENT_REQUESTS", "5"))

    # ============================================
    # Orchestrator Config
    # ============================================
    @property
    def orchestrator_config(self) -> dict:
        """Словарь конфигурации для передачи в Orchestrator."""
        return {
            "stt_model": self.STT_MODEL,
            "stt_language": self.STT_LANGUAGE,
            "device": None if self.STT_DEVICE == "auto" else self.STT_DEVICE,
            "use_gpu": self.USE_GPU,
            "topics": self.topics_list,
            "summarizer_algorithm": self.SUMMARIZER_ALGORITHM,
            "summarizer_language": self.SUMMARIZER_LANGUAGE,
            "max_summary_sentences": self.MAX_SUMMARY_SENTENCES,
        }

    def __init__(self):
        """Создаёт необходимые папки при инициализации."""
        self.audio_dir_abs.mkdir(parents=True, exist_ok=True)
        (BASE_DIR / "data" / "logs").mkdir(parents=True, exist_ok=True)

        # Проверка наличия обязательных переменных
        if not self.BOT_TOKEN:
            raise ValueError("BOT_TOKEN не задан! Проверьте файл .env")

    def __repr__(self) -> str:
        return f"Settings(BOT_TOKEN={self.BOT_TOKEN[:10]}..., DEBUG={self.DEBUG})"


# Создаём глобальный объект настроек (синглтон)
settings = Settings()