import uuid

import structlog
from fastapi import APIRouter, Depends, Request, status

from app.api.dependencies import limiter, verify_api_key
from app.domain.exceptions import AnalysisError, TextTooLongError, TextTooShortError
from app.domain.models import AnalyzeRequest, AnalyzeResponse
from app.services.text_analyzer import TextAnalyzerService

router = APIRouter(tags=["Analysis"])

# single service instance shared across requests (stateless)
_service = TextAnalyzerService()


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze text",
    description=(
        "Accepts text and returns sentiment, top keywords, word/character counts, "
        "and an optional AI-generated summary.\n\n"
        "**Authentication:** requires `X-API-Key` header.\n"
        "**Rate limit:** 10 requests per minute per IP."
    ),
)
@limiter.limit("10/minute")
async def analyze_text(
    request: Request,  # slowapi needs the request object
    body: AnalyzeRequest,
    _api_key: str = Depends(verify_api_key),
) -> AnalyzeResponse:
    request_id = str(uuid.uuid4())
    log = structlog.get_logger(__name__).bind(request_id=request_id)
    log.info("analyze_request_received", text_length=len(body.text))

    try:
        result = await _service.analyze(body.text)
    except (TextTooShortError, TextTooLongError) as exc:
        log.warning("validation_error", detail=str(exc))
        raise
    except AnalysisError as exc:
        log.error("analysis_error", detail=str(exc))
        raise

    log.info("analyze_request_complete", sentiment=result.sentiment)
    return result
