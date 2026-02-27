import re
from collections import Counter

from openai import AsyncOpenAI, OpenAIError

from app.core.config import settings
from app.core.logging import get_logger
from app.core.metrics import ANALYSES_ERRORS_TOTAL, ANALYSES_TOTAL
from app.domain.exceptions import AnalysisError, TextTooLongError, TextTooShortError
from app.domain.models import AnalyzeResponse

logger = get_logger(__name__)

# common English words we skip when picking keywords
_STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "are", "was", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "could", "should", "may", "might", "this", "that", "these",
    "those", "it", "its", "i", "you", "he", "she", "we", "they", "them",
    "their", "our", "not", "no", "so", "if", "than", "then", "also",
}

_POSITIVE_WORDS = {
    "good", "great", "excellent", "amazing", "awesome", "fantastic",
    "wonderful", "brilliant", "perfect", "love", "best", "happy", "glad",
    "positive", "outstanding", "superior", "impressive", "remarkable",
    "innovative", "efficient", "powerful", "fast", "easy", "simple",
    "helpful", "useful", "nice", "beautiful", "smart", "clean",
}

_NEGATIVE_WORDS = {
    "bad", "terrible", "awful", "horrible", "worst", "hate", "poor",
    "negative", "wrong", "broken", "slow", "hard", "difficult", "ugly",
    "complex", "confusing", "useless", "boring", "annoying", "error",
    "fail", "failure", "bug", "crash", "problem", "issue", "lack",
}


class TextAnalyzerService:
    """Handles all text analysis logic. Stateless, so one instance is enough."""

    def __init__(self) -> None:
        # only create the OpenAI client if we actually have a key
        self._openai_client: AsyncOpenAI | None = (
            AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            if settings.OPENAI_API_KEY
            else None
        )

    async def analyze(self, text: str) -> AnalyzeResponse:
        if len(text) < 5:
            raise TextTooShortError()
        if len(text) > 5000:
            raise TextTooLongError()

        words = self._tokenise(text)
        word_count = len(words)
        char_count = len(text)
        keywords = self._top_keywords(words)
        sentiment, score = self._rule_based_sentiment(words)
        ai_summary: str | None = None
        model_used = "rule-based-mock"

        if self._openai_client:
            try:
                sentiment, score, ai_summary, model_used = await self._openai_analyze(
                    text, sentiment, score
                )
            except OpenAIError as exc:
                # if OpenAI fails, just fall back to the rule-based result
                logger.warning("openai_fallback", reason=str(exc))
                ANALYSES_ERRORS_TOTAL.labels(error_type="openai_error").inc()

        ANALYSES_TOTAL.labels(sentiment=sentiment).inc()
        logger.info(
            "analysis_complete",
            word_count=word_count,
            sentiment=sentiment,
            model_used=model_used,
        )

        return AnalyzeResponse(
            sentiment=sentiment,
            sentiment_score=round(score, 4),
            keywords=keywords,
            word_count=word_count,
            char_count=char_count,
            ai_summary=ai_summary,
            model_used=model_used,
        )

    @staticmethod
    def _tokenise(text: str) -> list[str]:
        """Split text into lowercase words, removing stop words and punctuation."""
        return [
            w for w in re.findall(r"[a-zA-Z']+", text.lower())
            if w not in _STOP_WORDS and len(w) > 1
        ]

    @staticmethod
    def _top_keywords(words: list[str], n: int = 5) -> list[str]:
        if not words:
            return []
        return [word for word, _ in Counter(words).most_common(n)]

    @staticmethod
    def _rule_based_sentiment(words: list[str]) -> tuple[str, float]:
        pos = sum(1 for w in words if w in _POSITIVE_WORDS)
        neg = sum(1 for w in words if w in _NEGATIVE_WORDS)
        total = len(words) or 1
        score = (pos - neg) / total

        if score > 0.05:
            return "positive", min(score * 5, 1.0)
        if score < -0.05:
            return "negative", max(score * 5, -1.0)
        return "neutral", score

    async def _openai_analyze(
        self,
        text: str,
        fallback_sentiment: str,
        fallback_score: float,
    ) -> tuple[str, float, str, str]:
        """Send the text to OpenAI and parse the response. Falls back to rule-based on parse errors."""
        client = self._openai_client
        assert client is not None

        system_prompt = (
            "You are a text-analysis assistant. "
            "Reply ONLY with valid JSON matching this schema: "
            '{"sentiment": "positive"|"neutral"|"negative", '
            '"score": <float -1.0 to 1.0>, '
            '"summary": "<one sentence>"}'
        )
        try:
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text[:2000]},
                ],
                temperature=0,
                max_tokens=120,
                response_format={"type": "json_object"},
            )
        except Exception as exc:
            raise AnalysisError(str(exc)) from exc

        import json

        raw = response.choices[0].message.content or "{}"
        try:
            data = json.loads(raw)
            sentiment = data.get("sentiment", fallback_sentiment)
            score = float(data.get("score", fallback_score))
            summary = data.get("summary", "")
        except (ValueError, KeyError):
            sentiment, score, summary = fallback_sentiment, fallback_score, ""

        model_label = f"openai:{settings.OPENAI_MODEL}"
        return sentiment, score, summary or None, model_label
