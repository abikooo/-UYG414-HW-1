from typing import Literal

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=5,
        max_length=5000,
        description="Text to analyze (between 5 and 5000 characters).",
        examples=["FastAPI is a great framework for building REST APIs in Python!"],
    )
    language_hint: str = Field(
        default="en",
        description="ISO-639-1 language code, used as a hint only.",
        examples=["en", "tr"],
    )


class AnalyzeResponse(BaseModel):
    sentiment: Literal["positive", "neutral", "negative"] = Field(
        ...,
        description="Detected sentiment of the input text.",
    )
    sentiment_score: float = Field(
        ...,
        ge=-1.0,
        le=1.0,
        description="Score from -1.0 (very negative) to +1.0 (very positive).",
    )
    keywords: list[str] = Field(
        ...,
        description="Top 5 keywords found in the text.",
    )
    word_count: int = Field(..., description="Number of words in the text.")
    char_count: int = Field(..., description="Number of characters in the text.")
    ai_summary: str | None = Field(
        default=None,
        description="One-sentence summary from OpenAI. Only present if OPENAI_API_KEY is set.",
    )
    model_used: str = Field(
        ...,
        description="Which model was used: 'openai:<model>' or 'rule-based-mock'.",
    )


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    version: str
    service: str
