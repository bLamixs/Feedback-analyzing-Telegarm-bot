import pytest
from services.summarization import SummarizationService


@pytest.mark.asyncio
async def test_summarize_long_text():
    summarizer = SummarizationService(default_algorithm="lsa")
    long_text = " ".join(["предложение " + str(i) for i in range(50)])
    summary = await summarizer.summarize_simple(long_text, sentences_count=2)
    assert len(summary.split()) <= 30
    assert isinstance(summary, str)


@pytest.mark.asyncio
async def test_summarize_short_text():
    summarizer = SummarizationService()
    short = "очень короткий текст"
    result = await summarizer.summarize_simple(short)
    # Если текст слишком короткий, возвращается оригинал
    assert result == short