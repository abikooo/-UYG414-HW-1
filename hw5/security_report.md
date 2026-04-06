# HW#5 Security & AI Design Report

## 1. Advanced Security Implementation

### 1.1 Secure Authentication & RBAC
- **JWT-based Authentication**: Implemented via `auth_service` using `HS256` algorithm and `bcrypt` for secure password hashing.
- **Role-Based Access Control (RBAC)**: The API Gateway extracts roles from JWT claims and propagates them via `X-User-Role` headers. Downstream services (like `log_service`) use these headers to enforce permissions (e.g., `require_writer_role` for log ingestion).
- **Refresh Token Strategy**: Implemented refresh tokens with a 7-day TTL to allow secure session persistence without requiring frequent re-authentication.

### 1.2 Rate Limiting (Centralized & Per-Service)
- **API Gateway Rate Limiting**: Integrated `slowapi` at the gateway level.
- **Global Policy**: 10 requests per minute per IP for sensitive routes (e.g., `/auth/register`) to prevent brute-force attacks.
- **Burst Handling**: The limiter ensures that spikes in traffic from a single source do not degrade service for other tenants.

### 1.3 Secure Secrets Management
- **Environment Separation**: Secrets are handled via `.env` files and environment variables, ensuring no sensitive data is hardcoded in the repository.
- **Production Best Practices**: In the Kubernetes deployment (Stage 3), secrets are managed via `k8s-secrets` which are encrypted at rest in the etcd store. For production environments, we recommend integration with **AWS Secrets Manager** or **HashiCorp Vault**.

---

## 2. AI Functionality: Hybrid Security Observation

### 2.1 Two-Tiered AI Architecture
To ensure both **real-time performance** and **high-quality reasoning**, we implemented a two-tier AI processing pipeline:

#### Tier 1: Local Fast-Lane Anomaly Detection (PyTorch)
- **Model**: Custom MLP-based Autoencoder implemented in [services/local_ml_service.py](file:///c:/Users/seiil/Desktop/abiko/special-topics/project/log_service/services/local_ml_service.py).
- **Performance**: <1ms inference per log entry.
- **Functionality**: Identifies novel or structural anomalies in any log entry (including INFO logs) at the point of ingestion.

#### Tier 2: Deep Semantic Analysis (Anthropic Claude-3)
- **Trigger**: Activated by high anomaly scores from Tier 1 or critical error levels.
- **Functionality**: A specialized endpoint `/api/v1/logs/anomalies` that performs:
    - **Threat Analysis**: Detailed root-cause hypothesis and potential security threat classification.
    - **Summarization**: Turning batches of recent logs into natural language incident reports.

### 2.2 Feature: Intelligent Log Classification
Every log is first checked by the local PyTorch model. If a log is flagged as anomalous or is a critical error, it is forwarded to the Claude-3 engine for deep semantic classification (e.g., `DATABASE_ERROR`, `AUTH_ERROR`).

---

## 3. Updated Architecture Diagram

```mermaid
graph TD
    User((User)) -->|HTTPS| Gateway[API Gateway]
    
    subgraph "Security Layer"
        Gateway -->|Rate Limit| Limiter[SlowAPI]
        Gateway -->|Validate| AuthReq[Auth Validation]
    end
    
    Gateway -->|JWT Token| AuthSvc[Auth Service]
    AuthSvc -->|PostgreSQL| AuthDB[(Auth DB)]
    
    LogSvc -->|1. Fast Anomaly Check| Torch[Local PyTorch ML]
    LogSvc -->|2. Deep Analysis (If Anomaly)| AISvc[AI Engine - Claude]
    
    LogSvc -->|PostgreSQL| LogDB[(Logs DB)]
    
    LogSvc -->|Critical Events| NotifSvc[Notification Service]
```

## 4. AI Feature Demonstration
To demonstrate the anomaly detection:
1. Ingest several logs simulating a failed login spree.
2. Call `POST /api/v1/logs/anomalies` via the API Gateway.
3. The response will contain a structured analysis of the potential threat and a severity score.
