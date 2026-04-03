# LogAI Suite: Intelligent Microservice Ecosystem

Welcome to the LogAI Suite—a sophisticated, cloud-native project designed to rethink how we handle system logs. Instead of treating logs as static text files, this system treats them as actionable intelligence.

Developed as part of the UYG414 Special Topics in Software Development course, this ecosystem has evolved from a single service into a fully-orchestrated stack of professional-grade microservices.

### What makes it special?
- AI-Powered Analysis: Integrated with Anthropic's Claude AI to automatically classify errors and provide human-readable incident summaries.
- Distributed by Design: A multi-service architecture communicating via REST and asynchronous messaging.
- Production Ready: Built with modern DevOps practices, including Docker, Kubernetes, and GitHub Actions.

## Repo Structure
  ├── hw1/    — HW#1: Core Service
  ├── hw2/    — HW#2: Distributed System
  ├── hw3/    — HW#3: Production (K8s & CI/CD)
  ├── hw4/    — HW#4: Observability (ELK & OTEL)
  ├── project/— Evolution (Cumulative Latest)
  ├── .github/ — CI/CD Pipeline
  └── README.md

## Stage 1 — HW#1: Core Service
I built an API using FastAPI. It has a clean four-layer architecture. It stores logs in PostgreSQL using SQLAlchemy. Error logs trigger an Anthropic Claude API call. This classifies the error type. Authentication uses a static API key header.

Method | Path | Description
---|---|---
POST | `/api/v1/logs` | Ingest a log entry
GET | `/api/v1/logs` | List logs with filters
GET | `/api/v1/logs/{id}` | Get a single log and its AI classification
POST | `/api/v1/logs/analyze` | Request a batch summary incident report from Claude
GET | `/api/v1/health` | Health check endpoint
GET | `/api/v1/metrics` | Retrieve observability telemetry

How to run:
```bash
cd hw1
cp .env.example .env
docker-compose up --build
```

## Stage 2 — HW#2: Distributed System
The project is a distributed microservice system inside Docker Compose. An API Gateway handles incoming traffic. It routes requests. An Auth Service issues and checks JWTs. A Notification Service listens to RabbitMQ for critical logs. The Log Service publishes messages to RabbitMQ. It also checks JWT roles before saving a log.

Service | Port | What it does
---|---|---
Gateway | 8000 | Routes HTTP requests and checks JWTs
Auth | 8001 | Handles user registration and token issues
Log | 8002 | Stores logs and queries the Anthropic API
Notification | 8003 | Listens to RabbitMQ and saves critical alerts

Service | Method | Path | Auth | Description
---|---|---|---|---
Gateway | POST | `/auth/register` | No | Creates a user account
Gateway | POST | `/auth/login` | No | Issues access and refresh tokens
Gateway | POST | `/auth/refresh` | No | Exchanges a refresh token for new access
Gateway | GET | `/auth/verify` | Yes | Validates a user session
Gateway | GET | `/auth/me` | Yes | Returns the user profile
Gateway | POST | `/api/v1/logs` | Yes (Writer) | Ingests a new log entry
Gateway | GET | `/api/v1/logs` | Yes | Returns lists of past logs
Gateway | GET | `/api/v1/logs/{id}` | Yes | Returns a single log
Gateway | POST | `/api/v1/logs/analyze` | Yes | Generates an AI summary for recent logs
Gateway | GET | `/api/v1/health` | No | Checks Gateway health
Gateway | GET | `/api/v1/metrics` | Yes | Returns ingestion metrics
Notification | GET | `/notifications` | No | Returns past critical alerts

Gateway-to-service calls use REST. Clients need immediate responses for auth and ingestion workflows. RabbitMQ handles notifications. Notifications are background tasks. Clients omit waiting for background notifications. RabbitMQ stores the messages safely. The Notification Service reads them later. 

How to run:
```bash
cd hw2
cp .env.example .env
docker-compose up --build
```

## Stage 3 — HW#3: Production Deployment & DevOps
The project was migrated to a production-ready stack with automated lifecycle management. I added a CI/CD pipeline using GitHub Actions. It runs tests and builds Docker images on every push. I also created Kubernetes manifests for cloud-native orchestration. Standardized health checks were added across all services for monitoring.

### Key DevOps Features:
- **CI/CD**: GitHub Actions workflow in `.github/workflows/main.yml`.
- **Testing**: Automated unit tests using `pytest` and `httpx`.
- **Orchestration**: Kubernetes manifests in `project/k8s/` for Deployments, Services, ConfigMaps, and Secrets.
- **Environment Management**: Decoupled configuration using K8s primitives.

How to run tests:
```bash
cd project/api_gateway
python -m pytest
```

How to deploy (Kubernetes):
```bash
cd project
kubectl apply -f k8s/config.yaml
kubectl apply -f k8s/infrastructure.yaml
kubectl apply -f k8s/services.yaml
```

## Stage 4 — HW#4: Observability & Reliability Engineering
I made the system monitorable and fault tolerant. I added a centralized logging stack using Elasticsearch, Logstash, and Kibana. Services now send logs to Logstash asynchronously. I integrated OpenTelemetry for distributed tracing. This lets me see the request flow between services in Jaeger. I added Prometheus to scrape metrics from every service. I used Grafana to build a monitoring dashboard. I also improved the health checks. They now verify if the database is reachable. I added retry logic to the API Gateway using the Tenacity library. It automatically retries failed requests to downstream services.

### Observability Tools:
- **Centralized Logging**: ELK Stack (Elasticsearch, Logstash, Kibana) for log aggregation.
- **Metrics**: Prometheus for data collection and Grafana for visualization.
- **Tracing**: OpenTelemetry and Jaeger for request flow analysis.
- **Fault Tolerance**: Retries for transient failures and robust health probes.

Tool | Port | Purpose
---|---|---
Kibana | 5601 | Log search and visualization
Grafana | 3000 | Metrics dashboards
Prometheus | 9090 | Metrics collection engine
Jaeger | 16686 | Distributed tracing UI
OTEL Collector | 4317 | OpenTelemetry data receiver

## Environment Variables
Variable | Used In | Description | Example
---|---|---|---
`PROJECT_NAME` | HW1, HW2 | Application title | `Log Intelligence Service`
`API_KEY` | HW1 | Static key for API header | `dev-secret-key`
`DATABASE_URL` | HW1, HW2 | PostgreSQL connection string | `postgresql://postgres:pass@db:5432/db_name`
`ANTHROPIC_API_KEY` | HW1, HW2 | Key for Claude API | `sk-ant...`
`CLAUDE_MODEL` | HW1, HW2 | Claude text model string | `claude-3-haiku...`
`POSTGRES_PASSWORD` | HW1, HW2 | PostgreSQL database password | `postgres`
`AUTH_SERVICE_URL` | HW2 | URL the gateway uses to reach auth | `http://auth-service:8001`
`LOG_SERVICE_URL` | HW2 | URL the gateway uses to reach logs | `http://log-service:8002`
`JWT_SECRET_KEY` | HW2 | String used to sign JWTs | `demo-secret-key`
`JWT_ALGORITHM` | HW2 | Algorithm used for JWT signatures | `HS256`
`ACCESS_TOKEN_EXPIRE_MINUTES` | HW2 | Number of minutes before a JWT expires | `1440`
`RABBITMQ_URL` | HW2 | Connection string for RabbitMQ broker | `amqp://guest...`

## Assignment Coverage
Requirement | Where | Stage
---|---|---
Clean Architecture | api, services, repositories, models folders | 1, 2
REST API Design | HTTP endpoints using FastAPI | 1, 2
Containerization | Dockerfiles and docker-compose.yml | 1, 2
Service Communication | httpx for sync and aio-pika for async | 2
API Gateway | api_gateway Python app | 2
Authentication / Authorization | API Key (HW1) and JWT with Roles (HW2) | 1, 2
Async Messaging (RabbitMQ) | log_service pushing to notification_service | 2
AI Integration | Anthropic API in log_service | 1, 2
Observability | structlog JSON formatting and /metrics endpoint | 1, 2
Security basics | bcrypt password hashes and slowapi rate limits | 1, 2
CI/CD Pipeline | GitHub Actions workflow | 3
Automated Testing | pytest suite in each service | 3
Container Orchestration | Kubernetes manifests (Deployments/Services) | 3
Environment Config | ConfigMaps and Secrets | 3
Centralized Logging | ELK Stack (Logstash integration) | 4
Metrics Monitoring | Prometheus and Grafana dashboards | 4
Distributed Tracing | OpenTelemetry SDK and Jaeger | 4
Health Checks | Database and dependency validation | 4
Failure Handling | Tenacity retries and robust error recovery | 4
