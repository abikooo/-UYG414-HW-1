# SmartText API

UYG414 — HW#1

A text analysis microservice built with Python and FastAPI. You send it a piece of text and it tells you the sentiment, top keywords, and word/character counts. If an OpenAI key is provided it also generates a short summary using GPT-4o-mini; otherwise it falls back to a simple rule-based classifier.

---

## What's inside

```
smarttext-api/
├── app/
│   ├── main.py               # app setup, middleware, exception handlers
│   ├── core/                 # config, logging, metrics
│   ├── domain/               # pydantic models and custom exceptions
│   ├── services/             # business logic (no FastAPI imports here)
│   └── api/                  # routes and auth dependency
├── tests/
│   ├── test_api.py           # integration tests with TestClient
│   └── test_services.py      # unit tests for the analyzer
├── Dockerfile
├── docker-compose.yml        # API + Prometheus together
└── .github/workflows/ci.yml  # lint, test, docker build on every push
```

The service layer has no knowledge of HTTP or Prometheus — it just takes a string and returns a typed response. That separation is intentional (clean architecture).

---

## Running locally

```bash
# create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux

# install dependencies
pip install -r requirements.txt

# copy .env template and fill in your values
copy .env.example .env

# start the server
uvicorn app.main:app --reload
```

The API is at `http://localhost:8000` and Swagger docs are at `http://localhost:8000/docs`.

---

## Running with Docker

```bash
docker-compose up --build
```

This starts the API on port 8000 and Prometheus on port 9090. Prometheus is pre-configured to scrape the `/metrics` endpoint.

---

## Endpoints

### GET /api/v1/health
No authentication required.

```bash
curl http://localhost:8000/api/v1/health
# {"status":"ok","version":"1.0.0","service":"SmartText API"}
```

### POST /api/v1/analyze
Requires the `X-API-Key` header (default value: `dev-secret-key`).

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "X-API-Key: dev-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"text": "FastAPI is a great framework for building REST APIs in Python!"}'
```

Example response:
```json
{
  "sentiment": "positive",
  "sentiment_score": 0.3571,
  "keywords": ["fastapi", "great", "framework", "building", "rest"],
  "word_count": 11,
  "char_count": 65,
  "ai_summary": null,
  "model_used": "rule-based-mock"
}
```

Error codes:
| Code | Reason |
|---|---|
| 403 | Wrong or missing `X-API-Key` |
| 422 | Text is under 5 or over 5000 characters |
| 429 | More than 10 requests per minute from your IP |
| 502 | OpenAI returned an error |

### GET /metrics
Prometheus metrics. Includes request counts, latency histograms, and custom analysis counters.

---

## Configuration

Copy `.env.example` to `.env` and update the values you need:

| Variable | Default | Notes |
|---|---|---|
| `API_KEY` | `dev-secret-key` | Change this in production |
| `OPENAI_API_KEY` | _(empty)_ | Leave empty to use the rule-based fallback |
| `OPENAI_MODEL` | `gpt-4o-mini` | Any OpenAI chat model works |
| `LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, or `ERROR` |
| `DEBUG` | `false` | Enables FastAPI debug mode |

---

## Running tests

```bash
pytest tests/ -v
```

All 24 tests should pass. No network access or OpenAI key needed.

---

## CI/CD

GitHub Actions runs three jobs on every push and pull request:

1. **lint** — runs `ruff` to check code style
2. **test** — runs `pytest` with the virtual environment
3. **docker-build** — builds the Docker image to make sure it compiles

The workflow file is at `.github/workflows/ci.yml`.

---

## Security notes

- Authentication is done via the `X-API-Key` header. The key is set through the `API_KEY` environment variable.
- Rate limiting is handled by `slowapi` — 10 requests per minute per IP by default.
- Input validation is done by Pydantic before the request even reaches the service layer.
- The Docker container runs as a non-root user (`appuser`).
- CORS is set to `allow_origins=["*"]` for development — tighten this in production.
