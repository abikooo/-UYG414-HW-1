# Reliability and Observability Report

## 1. Overview
The microservice architecture has been enhanced with enterprise-grade observability and reliability features, focusing on monitoring, logging, tracing, and fault tolerance.

## 2. Infrastructure Setup
### Observability Stack
A centralized observability stack was deployed using Docker Compose:
- **ELK Stack**: Centralized logging using Elasticsearch (Storage), Logstash (Processing), and Kibana (Visualization).
- **Prometheus & Grafana**: Metrics collection and real-time visualization dashboards.
- **OpenTelemetry Collector**: To receive traces and metrics from all services and export them to Jaeger and Prometheus.
- **Jaeger**: Distributed tracing backend for request flow analysis.

## 3. Implemented Features
### Metrics Monitoring
- **Prometheus**: Configured to scrape all service endpoints.
- **Service Instrumentation**: `prometheus-fastapi-instrumentator` was added to all services to expose `/metrics`.

### Distributed Tracing
- **OpenTelemetry SDK**: Integrated into all microservices via a common `telemetry.py` setup.
- **Automatic Instrumentation**: FastAPI request/response lifecycle is automatically traced across service boundaries.

### Centralized Logging
- **Logstash Integration**: Services now use an asynchronous Logstash handler (`python-logstash-async`) to push structured logs to the ELK stack.
- **Consolidated View**: Kibana provides a unified interface to query logs across all microservices (available at port 5601).

### Health Checks
- **Automated Probes**: Each service now includes a `/health` endpoint that validates its own status and its dependency on the database.
- **Status Indicators**:
    - `healthy`: Service and dependencies are operational.
    - `degraded`: Service is running but one or more critical dependencies (e.g., Database) are down.

### Failure Handling Strategies
- **Retry Mechanisms**: `tenacity` library is integrated into the API Gateway to handle transient failures when calling downstream services.
- **Network Resilience**: Added health check probes in `docker-compose` to ensure services only start once their dependencies (PostgreSQL, RabbitMQ, Elasticsearch) are healthy.

## 4. Operational URLs
| Tool | URL |
|------|-----|
| Kibana (Logs) | http://localhost:5601 |
| Grafana (Metrics) | http://localhost:3000 |
| Prometheus | http://localhost:9090 |
| Jaeger (Tracing) | http://localhost:16686 |
| RabbitMQ Management | http://localhost:15672 |
