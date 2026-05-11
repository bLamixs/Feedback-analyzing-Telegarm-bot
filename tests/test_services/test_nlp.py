import pytest
from services.nlp_analysis import NLPService


@pytest.mark.asyncio
async def test_nlp_analyze_positive():
    nlp = NLPService(use_gpu=False)
    # Реальный анализ короткого русского текста
    result = await nlp.analyze("отлично, всё работает")
    assert result.sentiment.label in ("positive", "neutral")
    assert result.topic.topic is not None


@pytest.mark.asyncio
async def test_nlp_analyze_negative():
    nlp = NLPService(use_gpu=False)
    result = await nlp.analyze("всё сломалось, помогите")
    assert result.sentiment.label == "negative"
    assert result.intent.has_help_request is True


# Тест с моком моделей (быстрее)
@pytest.mark.asyncio
async def test_nlp_with_mocks():
    with patch("services.nlp_analysis.sentiment.pipeline") as mock_pipeline, \
         patch("services.nlp_analysis.topic.SentenceTransformer") as mock_topic:
        mock_pipeline.return_value = lambda x: [{"label": "negative", "score": 0.99}]
        mock_topic.return_value.encode.return_value = [0.1, 0.2]
        nlp = NLPService(use_gpu=False)
        # Переопределяем внутренние модели
        nlp.sentiment.pipeline = mock_pipeline.return_value
        result = await nlp.analyze("тест")
        assert result.sentiment.label == "negative"