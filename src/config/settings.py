"""
Конфигурация приложения.
Загружает переменные из .env (в корне проекта) и предоставляет их в типобезопасном виде.
"""

import os
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator

# Загружаем переменные из .env, расположенного в корне проекта
load_dotenv()

class Settings(BaseModel):
    # ----- Telegram -----
    BOT_TOKEN: str = Field(..., description="Токен Telegram бота")

    # ----- База данных -----
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./data/cyber_secretary.db",
        description="URL подключения к БД"
    )

    # ----- Администратор -----
    ADMIN_ID: int = Field(default=0, description="Telegram ID администратора")

    # ----- Отладка -----
    DEBUG: bool = Field(default=False, description="Режим отладки")
    LOG_LEVEL: str = Field(default="INFO", description="Уровень логирования")

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR"}
        if v.upper() not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of {allowed}")
        return v.upper()

    # ----- STT (Whisper) -----
    STT_MODEL: str = Field(default="base", description="Модель Whisper")
    STT_LANGUAGE: str = Field(default="ru", description="Язык распознавания")
    STT_DEVICE: Optional[str] = Field(default=None, description="cpu / cuda / auto")

    @field_validator("STT_MODEL")
    @classmethod
    def validate_stt_model(cls, v: str) -> str:
        allowed = {"tiny", "base", "small", "medium", "large"}
        if v.lower() not in allowed:
            raise ValueError(f"STT_MODEL must be one of {allowed}")
        return v.lower()

    # ----- NLP -----
    USE_GPU: bool = Field(default=True, description="Использовать GPU для NLP")
    NLP_TOPICS: str = Field(
        default="техническая поддержка,жалоба на сервис,предложение по улучшению,просто отзыв,спам",
        description="Темы через запятую"
    )

    @property
    def topics_list(self) -> List[str]:
        return [t.strip() for t in self.NLP_TOPICS.split(",") if t.strip()]

    # ----- Суммаризация -----
    SUMMARIZER_ALGORITHM: str = Field(default="lsa", description="Алгоритм суммаризации")
    SUMMARIZER_LANGUAGE: str = Field(default="russian", description="Язык для sumy")
    MAX_SUMMARY_SENTENCES: int = Field(default=3, description="Максимум предложений")

    @field_validator("SUMMARIZER_ALGORITHM")
    @classmethod
    def validate_algorithm(cls, v: str) -> str:
        allowed = {"lsa", "textrank", "luhn", "edmundson"}
        if v.lower() not in allowed:
            raise ValueError(f"Must be one of {allowed}")
        return v.lower()

    # ----- Файлы и хранение -----
    BASE_DIR: Path = Path(__file__).parent.parent
    AUDIO_TEMP_DIR: Path = Field(default="data/audio", description="Папка для временных аудио")
    KEEP_AUDIO_FILES: bool = Field(default=False)
    MAX_AUDIO_AGE_HOURS: int = Field(default=24)

    @property
    def audio_dir_abs(self) -> Path:
        return self.BASE_DIR / self.AUDIO_TEMP_DIR

    # ----- Производительность -----
    MAX_CONCURRENT_REQUESTS: int = Field(default=5)

    # ----- Конфиг для оркестратора -----
    @property
    def orchestrator_config(self) -> dict:
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

    def model_post_init(self, __context):
        """Создаёт необходимые папки после загрузки настроек."""
        self.audio_dir_abs.mkdir(parents=True, exist_ok=True)
        (self.BASE_DIR / "data" / "logs").mkdir(parents=True, exist_ok=True)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()