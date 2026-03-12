# Log Intelligence Service
It ingests log entries and classifies error logs using Anthropic AI. It also sends notifications for critical events.

## Course
UYG414 Special Topics in Software Development — built incrementally across assignments.

## Repo Structure
  ├── hw1/    — HW#1: Core Service
  ├── hw2/    — HW#2: Distributed System
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
