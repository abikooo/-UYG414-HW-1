# syntax=docker/dockerfile:1

# Stage 1: install all Python dependencies into /install
FROM python:3.11-slim AS builder

WORKDIR /build

# copy requirements first so this layer gets cached unless deps change
COPY requirements.txt .

RUN pip install --upgrade pip \
 && pip install --prefix=/install --no-cache-dir -r requirements.txt


# Stage 2: lean runtime image
FROM python:3.11-slim AS runtime

LABEL maintainer="UYG414 Student"
LABEL version="1.0.0"
LABEL description="SmartText API"

# run as a non-root user for better security
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /app

COPY --from=builder /install /usr/local
COPY app/ ./app/

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
