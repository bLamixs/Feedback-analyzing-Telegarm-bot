# core/orchestrator.py

from src.services.NLP-service import NLPAnalysisService


class Orchestrator:
    def __init__(self):
        self.nlp_service = NLPAnalysisService(
            use_gpu=True,  # или False для CPU
            custom_topics=[  # свои темы
                "техническая поддержка",
                "жалоба на сервис",
                "предложение по улучшению",
                "просто отзыв",
                "спам"
            ]
        )

    async def process_text(self, text: str, user_id: int):
        # Анализируем текст
        result = await self.nlp_service.analyze(text)

        # Формируем ответ
        response = (
            f"📊 **Анализ сообщения**\n\n"
            f"📝 Текст: {text[:100]}...\n"
            f"😊 Тональность: {result.sentiment.label} ({result.sentiment.score:.2%})\n"
            f"📌 Тема: {result.topic.topic} ({result.topic.score:.2%})\n"
            f"🎯 Намерение: {result.intent.intent}\n"
            f"🆘 Просьба о помощи: {'Да' if result.intent.has_help_request else 'Нет'}\n"
            f"⏱ Время обработки: {result.processing_time_ms:.0f}мс"
        )

        return response