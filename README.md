# UYG414 Microservice Ecosystem — HW Assignment

This repository tracks the evolution of a multi-service log and notification system. Each directory represents a specific homework stage.

## Repo Structure
  ├── hw1/    — HW#1: Core Service
  ├── hw2/    — HW#2: Distributed System
  ├── hw3/    — HW#3: Production (K8s & CI/CD)
  ├── hw4/    — HW#4: Observability (ELK & OTEL)
  ├── hw5/    — HW#5: Security & AI (RBAC & Claude)
  ├── project/— Evolution (Cumulative Latest)
  ├── .github/ — CI/CD Pipeline
  └── README.md

## Stage 1 — HW#1: Core Service
I built an API using FastAPI. It has a clean four-layer architecture. It stores logs in PostgreSQL using SQLAlchemy. Error logs trigger an Anthropic Claude API call. This classifies the error type. Authentication uses a static API key header.

Method | Path | Description
---|---|---
POST | `/api/v1/logs` | Ingest a log entry
GET | `/api/v1/logs` | List logs with filters

## Stage 2 — HW#2: Distributed System
I split the monolith into microservices. They communicate via RabbitMQ and HTTP asynchronously.
- **API Gateway**: Route requests based on service and check global JWTs.
- **Auth Service**: Manages accounts and issues secure tokens.
- **Log Service**: Receives logs and performs AI classification.
- **Notification Service**: Listens for critical events on RabbitMQ and alerts appropriately.

## Stage 3 — HW#3: Infrastructure & CI/CD
Deployment automation for cloud readiness.
- **Kubernetes**: Included manifests for all services, databases, and message brokers.
- **CI/CD**: Developed a GitHub Actions pipeline that runs automated `pytest` suites on every push and build Docker images.

## Stage 4 — HW#4: Observability & Reliability
Production monitoring and fault-tolerance stack.
- **Centralized Logging**: ELK (Elasticsearch, Logstash, Kibana) integration.
- **Metrics**: Prometheus + Grafana dashboard.
- **Distributed Tracing**: OpenTelemetry + Jaeger.
- **Reliability**: Health checks and Tenacity retries on the gateway.

## Stage 5 — HW#5: Advanced Security & AI
I implemented a comprehensive security layer and an advanced AI observation feature. Distributed rate limiting was added to the API Gateway to prevent service abuse. Auth Service was strengthened with Role-Based Access Control (RBAC) and refresh token rotation. I also integrated an "AI Anomaly Detection" system that analyzes historical logs using semantic intelligence to identify potential security threats or cascading system failures.

### Assignment Coverage (Summary)

Feature | Implementation | Stage
---|---|---
Layered Arch | Clean Separation (API, Service, Repo, Model) | 1
AI Classification | Log analysis using Claude integration | 1
Microservices | Multi-service split with RabbitMQ | 2
API Gateway | Routing and centralized JWT auth | 2
K8s Deployment | Manifests for orchestration and storage | 3
CI/CD Pipeline | GitHub Actions with automated tests | 3
Centralized Logging | ELK Stack (Elasticsearch, Logstash, Kibana) | 4
Metrics Monitoring | Prometheus and Grafana dashboards | 4
Distributed Tracing | OpenTelemetry SDK and Jaeger | 4
Health Checks | Database and dependency validation | 4
Failure Handling | Tenacity retries and robust recovery | 4
Role-Based Auth | JWT RBAC and header propagation | 5
Rate Limiting | Global leaky-bucket rate limiting (SlowAPI) | 5
AI Anomaly Detect | Semantic pattern analysis of logs (Claude) | 5
Security Report | Detailed security and AI design report | 5
