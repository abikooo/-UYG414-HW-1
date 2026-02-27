from prometheus_client import Counter
from prometheus_fastapi_instrumentator import Instrumentator

# tracks how many analyses ran, broken down by sentiment result
ANALYSES_TOTAL = Counter(
    "smarttext_analyses_total",
    "Total number of text analyses performed",
    ["sentiment"],
)

# tracks failures separately so they're easy to alert on
ANALYSES_ERRORS_TOTAL = Counter(
    "smarttext_analyses_errors_total",
    "Total number of text analysis errors",
    ["error_type"],
)


def create_instrumentator() -> Instrumentator:
    return Instrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=True,
    )
