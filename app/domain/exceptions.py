class SmartTextBaseError(Exception):
    """Base class for all domain-level errors in this service."""

    http_status: int = 500
    default_message: str = "An unexpected error occurred."

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.default_message)
        self.message = message or self.default_message


class TextTooShortError(SmartTextBaseError):
    http_status = 422
    default_message = "Text must be at least 5 characters long."


class TextTooLongError(SmartTextBaseError):
    http_status = 422
    default_message = "Text must not exceed 5000 characters."


class AnalysisError(SmartTextBaseError):
    http_status = 502
    default_message = "The analysis backend returned an unexpected error."
