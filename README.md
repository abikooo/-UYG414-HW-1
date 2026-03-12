# Log Intelligence Service
This project operates as a microservice framework to ingest, analyze via AI, and selectively relay critical application logs.

## Course
UYG414 Special Topics in Software Development
This repo is built incrementally across assignments, each stage extending the last.

## What it does (Project Overview)
External traffic enters through the API Gateway on port 8000, which validates JWT tokens produced by the Auth Service. Validated requests are forwarded to the Log Service. When the Log Service ingests a "CRITICAL" level event, it publishes a RabbitMQ message to the Notification Service, ensuring alerts persist without stalling HTTP loops.

## Why Async vs REST
We chose REST for the Gateway-to-Service tier because authorization and ingestion are synchronous workflows. They require immediate client feedback on validity, like a 401 Unauthorized or 201 Created.

We use an asynchronous messaging mechanism via RabbitMQ for critical notifications to decouple downstream failure domains. If the Notification Service goes offline, RabbitMQ buffers the alerts, preventing an ingestion failure from cascading back up to the client submitting the log.

## Quick Start
```bash
cd project
cp .env.example .env
docker-compose up --build -d
```

## Architecture
```text
                                           ┌──────────────┐
                                           │ Auth Service │
                        ┌──> REST ────────>│ (Port 8001)  │
┌─────────────┐         │                  └──────────────┘
│ API Gateway │─────────┤
│ (Port 8000) │         │                  ┌──────────────┐          ┌──────────────────────┐
└─────────────┘         └──> REST ────────>│ Log Service  │── AMQP ─>│ Notification Service │
                                           │ (Port 8002)  │          │      (Port 8003)     │
                                           └──────────────┘          └──────────────────────┘
```

## How to run tests
You can verify the end-to-end functionality using curl commands.

Register a user:
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Developer", "email": "dev@example.com", "password": "pass", "role": "DEVELOPER"}'
```

Login:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "dev@example.com", "password": "pass"}'
```

Get current user profile:
```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

Post critical log (triggers alert):
```bash
curl -X POST http://localhost:8000/api/v1/logs \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"service_name": "payment", "level": "CRITICAL", "message": "Cluster memory leak imminent"}'
```

Verify notification was created:
```bash
curl -X GET http://localhost:8003/notifications
```

## Assignments (Stage definitions)

### Stage 1 — HW#1: Core Service
**What was built:**
A FastAPI service with a clean 4-layer architecture separating api, services, repositories, and models. The service provides REST endpoints for log ingestion and search metrics, backed by PostgreSQL models via SQLAlchemy. AI log classification is integrated via the Anthropic Claude API for errors. Access is enforced by API key auth middleware, rate-limited at 100 requests/minute, and requests are traced using structlog JSON logging.

### Stage 2 — HW#2: Distributed System
**What was built:**
A multi-service architecture encompassing four distinct services. An API Gateway handles incoming traffic and centrally validates JWTs via an adjacent Auth Service utilizing bcrypt hashing. A Notification Service was built to asynchronously consume RabbitMQ messages broadcasted by the Log Service during critical events. Role-based access logic intercepts unauthorized actions inside service controllers.

## Combined Endpoints
| Service | Method | Path | Auth Required | Description |
|---|---|---|---|---|
| Gateway | POST | `/auth/register` | No | Creates a user account and hashes credentials |
| Gateway | POST | `/auth/login` | No | Issues an access token and refresh token |
| Gateway | POST | `/auth/refresh` | No | Exchanges a refresh token for new access |
| Gateway | GET | `/auth/verify` | Yes | Retrieves user context by validating the session ID |
| Gateway | GET | `/auth/me` | Yes | Resolves the profile tied to the access token |
| Gateway | POST | `/api/v1/logs` | Yes (Writer) | Ingests a new log entry |
| Gateway | GET | `/api/v1/logs` | Yes | Fetches paginated lists of historical logs |
| Gateway | GET | `/api/v1/logs/{id}` | Yes | Locates a specific log |
| Gateway | POST | `/api/v1/logs/analyze` | Yes | Initiates batch log evaluation |
| Gateway | GET | `/api/v1/health` | No | Bypasses proxy checks directly |
| Gateway | GET | `/api/v1/metrics` | Yes | Returns service ingestion counts |
| Notification | GET | `/notifications` | No | Retrieves historical alerts |

## Environment Variables
| Variable | Used In | Description | Example |
|---|---|---|---|
| `PROJECT_NAME` | HW1, HW2 | Declares the internal service title variable | `Log Intelligence Service` |
| `API_KEY` | HW1 | Legacy key validating ingress in the monolith stage | `dev-secret-key` |
| `DATABASE_URL` | HW1, HW2 | PostgreSQL connection string | `postgresql://postgres:pass@db:5432/db_name` |
| `ANTHROPIC_API_KEY` | HW1, HW2 | Secret API credentials binding Anthropic requests | `sk-ant-api03...` |
| `CLAUDE_MODEL` | HW1, HW2 | Declares the specific Claude text model | `claude-3-haiku-20240307` |
| `POSTGRES_PASSWORD` | HW1, HW2 | Interpolates PostGres initialization password | `postgres` |
| `AUTH_SERVICE_URL` | HW2 | Determines downstream endpoints inside proxy | `http://auth-service:8001` |
| `LOG_SERVICE_URL` | HW2 | Determines downstream endpoints inside proxy | `http://log-service:8002` |
| `JWT_SECRET_KEY` | HW2 | Symmetric key initializing token payloads | `demo-secret-key` |
| `JWT_ALGORITHM` | HW2 | Sets the HS algorithm structure | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | HW2 | Lifetime limit in minutes for the tokens | `1440` |
| `RABBITMQ_URL` | HW2 | Target URL initializing internal AMQP queues | `amqp://guest:guest@rabbitmq:5672/` |

## Assignment Coverage
| Requirement | Implementation | Stage |
|---|---|---|
| Clean Architecture | 4-layer directory isolation mapping controllers to DB repos | 1, 2 |
| REST API Design | HTTP verbs matching explicit resources across logs/auth | 1, 2 |
| Containerization | Multistage Dockerfiles wrapped in composing specs | 1, 2 |
| Service Communication | httpx for sync, aio-pika for async decoupling | 2 |
| API Gateway | Single entrypoint routing proxy via FastAPI | 2 |
| Authentication / Authorization | JWT logic embedded with role-based restrictions | 1, 2 |
| Async Messaging (RabbitMQ) | Fire-and-forget payload relay during critical events | 2 |
| AI Integration | Anthropic text generation triggered via Claude API | 1, 2 |
| Observability (logging + metrics) | Structlog formatters paired with latencies cache | 1, 2 |
| Security basics | Password hashing (bcrypt) and request rate limits | 1, 2 |
