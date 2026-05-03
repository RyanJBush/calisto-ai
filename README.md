# Calisto AI

Calisto AI is a production-style monorepo for an enterprise Retrieval-Augmented Generation (RAG) knowledge platform.

## Monorepo Structure

```text
/backend   FastAPI API, RAG services, JWT auth, RBAC, tests
/frontend  React + Vite + Tailwind SaaS UI
/docs      Architecture and engineering guides
```

## Features

- **FastAPI backend** with JWT authentication and RBAC (`Admin`, `Member`, `Viewer`)
- **Multi-tenant domain models** — organizations, users, documents, chunks, chat sessions/messages
- **Hybrid retrieval** — vector similarity search + keyword BM25-style search blended with reranking
- **Semantic chunking** — paragraphs + sentence boundaries with configurable size and overlap
- **Metadata filtering** — filter by document, collection, section, and tags
- **Configurable top-k** retrieval with confidence scoring and citation coverage metrics
- **Citation-aware answers** — every answer is traced back to source chunks with highlighted evidence
- **Document ingestion pipeline** — PDF, TXT, and Markdown support; deduplication, PII redaction, chunk preview
- **Background ingestion jobs** with status tracking and retry logic
- **Admin analytics dashboard** — queries processed, avg latency, top documents, ingestion breakdown, audit logs
- **Seeded demo dataset** — 5 realistic enterprise documents pre-chunked and indexed for instant querying
- **React frontend** with polished SaaS layout: sidebar navigation, confidence badges, source preview panel, loading/error states
- **Docker Compose** deployment ready; SQLite for local dev, PostgreSQL-ready for production

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker + Docker Compose (optional, recommended)

### Local Development

```bash
make bootstrap
cp backend/.env.example backend/.env
make db-upgrade
make init
make run-backend   # http://localhost:8000
make run-frontend  # http://localhost:5173
```

### Fast Demo (< 2 minutes)

1. Start the backend and frontend as above.
2. Open **http://localhost:5173** and log in:
   - `admin@calisto.ai` / `password123`
3. Navigate to **Chat** and click one of the example query chips, e.g.:
   - *"What is the leave policy?"*
   - *"What is the escalation window for P1 incidents?"*
   - *"How fast do we respond to critical support tickets?"*
   - *"How often are performance reviews conducted?"*
   - *"What is the data retention period for customer documents?"*
4. Inspect the response:
   - **Confidence badge** (green/amber/red) based on retrieval scores
   - **Citation cards** with relevance %, section label, and chunk reference
   - **Source Preview panel** with highlighted evidence terms
   - **Latency breakdown** (rewrite → retrieval → answer)
   - **Feedback buttons** to rate answers
5. Go to **Documents** to upload a new file (PDF, TXT, or MD), preview chunks before indexing, and manage collections.
6. Visit **Dashboard** (admin only) for live platform metrics.

### Seeded Demo Documents

The `make init` command seeds 5 enterprise knowledge documents:

| Document | Content |
|---|---|
| Employee Handbook | Leave policy, remote work, expense policy, performance reviews, code of conduct |
| Security Operations Guide | P1–P4 incident levels, escalation procedures, vulnerability management, access control |
| Support SLA | Response/resolution time targets by plan, escalation procedure, SLA credits |
| Engineering Onboarding Guide | Dev workflow, tech stack, deployment process, on-call rotation |
| Data Retention Policy | Retention periods, backup policy, GDPR/CCPA compliance |

### Docker Compose

```bash
docker compose up --build
```

## Backend Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/api/auth/login` | Authenticate and receive JWT |
| GET | `/api/auth/me` | Current user profile |
| POST | `/api/documents/upload` | Upload document (PDF/TXT/MD) |
| POST | `/api/documents/preview-chunks` | Preview chunks before indexing |
| GET | `/api/documents` | List documents |
| GET | `/api/documents/{id}` | Document detail with chunks |
| GET | `/api/documents/{id}/ingestion-runs` | Ingestion run history |
| POST | `/api/chat/query` | Submit query, receive answer + citations |
| GET | `/api/chat/history` | Chat history |
| POST | `/api/chat/feedback` | Submit answer feedback |
| GET | `/api/admin/analytics/summary` | Platform analytics (admin) |

## Testing and Linting

```bash
make lint
make test
```

## Database Migrations

```bash
make db-upgrade
make db-downgrade
```

## Demo Credentials (Seeded)

| Email | Password | Role |
|---|---|---|
| `admin@calisto.ai` | `password123` | Admin |
| `member@calisto.ai` | `password123` | Member |
| `viewer@calisto.ai` | `password123` | Viewer |

## Architecture Overview

See:

- `/docs/ARCHITECTURE.md`
- `/docs/PORTS.md`
- `/docs/STYLEGUIDE.md`

## Roadmap

- Replace in-memory vector implementation with persistent FAISS index service
- Add pgvector provider implementation behind vector store interface
- Add SSO/SCIM integrations for enterprise identity workflows
- Add richer metrics dashboards with time-series charts
- Add OpenAI / Anthropic LLM provider behind the existing `LLMService` interface
