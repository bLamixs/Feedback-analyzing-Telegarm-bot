"""
Оркестратор — центральный координатор всех сервисов.

Отвечает за:
- Прием текстовых и голосовых сообщений
- Вызов STT (для голоса)
- Вызов NLP анализа
- Вызов суммаризации
- Сохранение в БД
- Формирование ответа пользователю
"""

import time
import logging
from typing import Optional, Dict, Any, Union

from src.services.STT import STTService
from src.services.NLP_service import NLPAnalysisService
from src.services.Summarisation_service import SummarizationService
from src.services.storage import StorageService

from .exceptions import ProcessingError, ServiceUnavailableError
from .models import ProcessedMessage, UserContext


class Orchestrator:
    """
    Оркестратор для "Кибер-секретаря".

    Координирует все модули бота.
    """

    def __init__(
            self,
            stt_service: Optional[STTService] = None,
            nlp_service: Optional[NLPAnalysisService] = None,
            summarization_service: Optional[SummarizationService] = None,
            storage_service: Optional[StorageService] = None,
            config: Optional[Dict] = None
    ):
        """
        Инициализация оркестратора.

        Args:
            stt_service: сервис распознавания речи
            nlp_service: сервис NLP анализа
            summarization_service: сервис суммаризации
            storage_service: сервис хранения данных
            config: дополнительные настройки
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}

        # Инициализация сервисов (создаем, если не переданы)
        self.stt = stt_service or self._init_stt()
        self.nlp = nlp_service or self._init_nlp()
        self.summarizer = summarization_service or self._init_summarizer()
        self.storage = storage_service or self._init_storage()

        self.logger.info("Orchestrator initialized successfully")

    def _init_stt(self) -> STTService:
        """Инициализация STT сервиса с настройками по умолчанию"""
        try:
            return STTService(
                model_name=self.config.get("stt_model", "base"),
                language=self.config.get("stt_language", "ru"),
                device=self.config.get("device", None)
            )
        except Exception as e:
            self.logger.error(f"Failed to init STT: {e}")
            raise ServiceUnavailableError(f"STT service unavailable: {e}")

    def _init_nlp(self) -> NLPAnalysisService:
        """Инициализация NLP сервиса"""
        try:
            return NLPAnalysisService(
                use_gpu=self.config.get("use_gpu", True),
                custom_topics=self.config.get("topics", None)
            )
        except Exception as e:
            self.logger.error(f"Failed to init NLP: {e}")
            raise ServiceUnavailableError(f"NLP service unavailable: {e}")

    def _init_summarizer(self) -> SummarizationService:
        """Инициализация сервиса суммаризации"""
        try:
            return SummarizationService(
                default_algorithm=self.config.get("summarizer_algorithm", "lsa"),
                language=self.config.get("summarizer_language", "russian"),
                max_sentences=self.config.get("max_summary_sentences", 3)
            )
        except Exception as e:
            self.logger.error(f"Failed to init summarizer: {e}")
            raise ServiceUnavailableError(f"Summarization service unavailable: {e}")

    def _init_storage(self) -> StorageService:
        """Инициализация сервиса хранения"""
        try:
            return StorageService()
        except Exception as e:
            self.logger.error(f"Failed to init storage: {e}")
            raise ServiceUnavailableError(f"Storage service unavailable: {e}")

    # ========================
    # Основные методы обработки
    # ========================

    async def process_text(
            self,
            text: str,
            user_context: UserContext,
            message_id: int
    ) -> str:
        """
        Обработка текстового сообщения.

        Args:
            text: текст сообщения
            user_context: контекст пользователя
            message_id: ID сообщения в Telegram

        Returns:
            ответ пользователю
        """
        start_time = time.time()

        try:
            self.logger.info(f"Processing text from user {user_context.user_id}: {text[:50]}...")

            # 1. NLP анализ
            nlp_result = await self.nlp.analyze(text)

            # 2. Суммаризация
            summary_result = await self.summarizer.summarize_simple(text)

            # 3. Сохраняем в БД
            processed_msg = ProcessedMessage(
                message_id=message_id,
                user_id=user_context.user_id,
                message_type="text",
                original_text=text,
                recognized_text=None,
                sentiment=nlp_result.sentiment.label,
                sentiment_score=nlp_result.sentiment.score,
                topic=nlp_result.topic.topic,
                topic_score=nlp_result.topic.score,
                intent=nlp_result.intent.intent,
                has_help_request=nlp_result.intent.has_help_request,
                summary=summary_result,
                processing_time_ms=(time.time() - start_time) * 1000
            )
            await self.storage.save_message(processed_msg)

            # 4. Формируем ответ
            response = self._build_response(
                original_text=text,
                nlp_result=nlp_result,
                summary=summary_result,
                processing_time=processed_msg.processing_time_ms
            )

            return response

        except Exception as e:
            self.logger.error(f"Text processing failed: {e}", exc_info=True)
            raise ProcessingError(f"Failed to process text: {e}")

    async def process_voice(
            self,
            audio_bytes: Union[bytes, str],
            user_context: UserContext,
            message_id: int,
            duration: float
    ) -> str:
        """
        Обработка голосового сообщения.

        Args:
            audio_bytes: аудиофайл (байты или путь)
            user_context: контекст пользователя
            message_id: ID сообщения
            duration: длительность аудио

        Returns:
            ответ пользователю
        """
        start_time = time.time()

        try:
            self.logger.info(f"Processing voice from user {user_context.user_id}, duration={duration}s")

            # 1. Распознавание речи (STT)
            if isinstance(audio_bytes, bytes):
                recognized_text = await self.stt.transcribe_simple(audio_bytes)
            else:
                recognized_text = await self.stt.transcribe_simple(audio_bytes)

            if not recognized_text:
                return "❌ Не удалось распознать речь. Пожалуйста, говорите четче или отправьте текстом."

            # 2. NLP анализ
            nlp_result = await self.nlp.analyze(recognized_text)

            # 3. Суммаризация
            summary_result = await self.summarizer.summarize_simple(recognized_text)

            # 4. Сохраняем в БД
            processed_msg = ProcessedMessage(
                message_id=message_id,
                user_id=user_context.user_id,
                message_type="voice",
                original_text=None,
                recognized_text=recognized_text,
                sentiment=nlp_result.sentiment.label,
                sentiment_score=nlp_result.sentiment.score,
                topic=nlp_result.topic.topic,
                topic_score=nlp_result.topic.score,
                intent=nlp_result.intent.intent,
                has_help_request=nlp_result.intent.has_help_request,
                summary=summary_result,
                processing_time_ms=(time.time() - start_time) * 1000
            )
            await self.storage.save_message(processed_msg)

            # 5. Формируем ответ
            response = self._build_response(
                original_text=recognized_text,
                nlp_result=nlp_result,
                summary=summary_result,
                processing_time=processed_msg.processing_time_ms,
                is_voice=True
            )

            return response

        except Exception as e:
            self.logger.error(f"Voice processing failed: {e}", exc_info=True)
            raise ProcessingError(f"Failed to process voice: {e}")

    # ========================
    # Вспомогательные методы
    # ========================

    def _build_response(
            self,
            original_text: str,
            nlp_result,
            summary: str,
            processing_time: float,
            is_voice: bool = False
    ) -> str:
        """
        Формирует красивое сообщение для пользователя.

        Args:
            original_text: распознанный/исходный текст
            nlp_result: результаты NLP анализа
            summary: краткое содержание
            processing_time: время обработки в мс
            is_voice: было ли голосовое сообщение

        Returns:
            форматированный ответ
        """
        # Эмодзи для тональности
        sentiment_emoji = {
            "positive": "😊",
            "negative": "😠",
            "neutral": "😐"
        }.get(nlp_result.sentiment.label, "🤔")

        # Эмодзи для срочности
        urgency_emoji = "🚨 " if nlp_result.intent.has_help_request else ""

        # Тип сообщения
        msg_type = "🎤 Голосовое" if is_voice else "📝 Текстовое"

        # Формируем ответ
        response = f"""
{msg_type} сообщение обработано! {sentiment_emoji}

📄 **Распознанный текст:**
_{original_text[:300]}{'...' if len(original_text) > 300 else ''}_

📊 **Анализ:**
• Тональность: **{nlp_result.sentiment.label}** ({nlp_result.sentiment.score:.1%})
• Тема: **{nlp_result.topic.topic}** ({nlp_result.topic.score:.1%})
• Намерение: **{nlp_result.intent.intent}**

📝 **Краткое содержание:**
_{summary}_

⏱ Время обработки: {processing_time:.0f} мс
        """.strip()

        # Добавляем предупреждение о просьбе помощи
        if nlp_result.intent.has_help_request:
            response = f"{urgency_emoji} **ВНИМАНИЕ: Обнаружена просьба о помощи!** {urgency_emoji}\n\n" + response

        return response

    # ========================
    # Методы для получения статистики
    # ========================

    async def get_user_history(self, user_id: int, limit: int = 10):
        """
        Получить историю сообщений пользователя.
        """
        return await self.storage.get_user_messages(user_id, limit)

    async def get_service_info(self) -> Dict[str, Any]:
        """
        Получить информацию о всех сервисах.
        """
        return {
            "orchestrator": "running",
            "stt": self.stt.get_model_info() if hasattr(self.stt, 'get_model_info') else "unknown",
            "nlp": self.nlp.get_service_info() if hasattr(self.nlp, 'get_service_info') else "unknown",
            "summarizer": self.summarizer.get_service_info() if hasattr(self.summarizer, 'get_service_info') else "unknown",
            "storage": "connected" if self.storage else "unknown"
        }

    async def health_check(self) -> bool:
        """
        Проверка работоспособности всех сервисов.
        """
        try:
            # Проверяем STT
            if self.stt is None:
                return False

            # Проверяем NLP
            test_result = await self.nlp.analyze("тест")
            if not test_result:
                return False

            # Проверяем суммаризатор
            test_summary = await self.summarizer.summarize_simple(
                "тестовое сообщение для проверки работы сервиса суммаризации"
            )
            if not test_summary:
                return False

            return True
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False