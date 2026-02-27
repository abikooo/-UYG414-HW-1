import pytest

from app.services.text_analyzer import TextAnalyzerService
from app.domain.exceptions import TextTooShortError, TextTooLongError


@pytest.fixture
def service() -> TextAnalyzerService:
    return TextAnalyzerService()


class TestTokenise:
    def test_removes_stop_words(self, service: TextAnalyzerService) -> None:
        words = service._tokenise("the quick brown fox")
        assert "the" not in words

    def test_lowercases(self, service: TextAnalyzerService) -> None:
        words = service._tokenise("Python PYTHON python")
        assert all(w == "python" for w in words)

    def test_strips_punctuation(self, service: TextAnalyzerService) -> None:
        words = service._tokenise("hello, world!")
        assert "hello" in words
        assert "world" in words


class TestTopKeywords:
    def test_returns_at_most_five(self, service: TextAnalyzerService) -> None:
        words = ["a", "b", "c", "d", "e", "f", "g"]
        assert len(service._top_keywords(words)) <= 5

    def test_most_frequent_first(self, service: TextAnalyzerService) -> None:
        words = ["python", "python", "python", "api", "api"]
        keywords = service._top_keywords(words)
        assert keywords[0] == "python"

    def test_empty_list(self, service: TextAnalyzerService) -> None:
        assert service._top_keywords([]) == []


class TestRuleBasedSentiment:
    def test_positive(self, service: TextAnalyzerService) -> None:
        words = ["amazing", "excellent", "great", "wonderful"]
        sentiment, score = service._rule_based_sentiment(words)
        assert sentiment == "positive"
        assert score > 0

    def test_negative(self, service: TextAnalyzerService) -> None:
        words = ["terrible", "awful", "horrible", "bad"]
        sentiment, score = service._rule_based_sentiment(words)
        assert sentiment == "negative"
        assert score < 0

    def test_neutral(self, service: TextAnalyzerService) -> None:
        words = ["table", "chair", "window", "door"]
        sentiment, _ = service._rule_based_sentiment(words)
        assert sentiment == "neutral"


class TestAnalyzeAsync:
    @pytest.mark.asyncio
    async def test_returns_correct_word_count(self, service: TextAnalyzerService) -> None:
        result = await service.analyze("FastAPI is great for building APIs quickly.")
        assert result.word_count > 0

    @pytest.mark.asyncio
    async def test_raises_on_short_text(self, service: TextAnalyzerService) -> None:
        with pytest.raises(TextTooShortError):
            await service.analyze("Hi")

    @pytest.mark.asyncio
    async def test_raises_on_long_text(self, service: TextAnalyzerService) -> None:
        with pytest.raises(TextTooLongError):
            await service.analyze("x" * 5001)

    @pytest.mark.asyncio
    async def test_model_used_is_mock(self, service: TextAnalyzerService) -> None:
        result = await service.analyze("This is a sample sentence for testing purposes.")
        assert result.model_used == "rule-based-mock"
