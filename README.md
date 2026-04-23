# Calisto AI

Calisto AI is a production-style monorepo for an enterprise Retrieval-Augmented Generation (RAG) knowledge platform.

## Monorepo Structure

```text
/backend   FastAPI API, RAG services, JWT auth, RBAC, tests
/frontend  React + Vite + Tailwind SaaS UI
/docs      Architecture and engineering guides
```

## Features (MVP)

- FastAPI backend with JWT authentication and RBAC (`Admin`, `Member`, `Viewer`)
- Multi-tenant-ready domain models (organizations, users, documents, chunks, chat sessions/messages)
- Document ingestion pipeline with chunking and embedding placeholders
- Retrieval + citation-aware answer composition
- React frontend with enterprise SaaS layout and core pages (Login, Dashboard, Documents, Chat, Settings)
- PostgreSQL-ready deployment with Docker Compose
- Local FAISS-style vector retrieval abstraction for MVP, designed for future `pgvector` swap
- Structured logging, health checks, and lightweight metrics
- CI workflow for backend lint/tests and frontend build validation

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
make run-backend
make run-frontend
```

Backend defaults to `http://localhost:8000`, frontend to `http://localhost:5173`.

### Docker Compose

```bash
docker compose up --build
```

## Backend Endpoints

- `GET /health`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/documents/upload`
- `POST /api/documents/upload-file` (multipart TXT/MD/JSON/PDF)
- `GET /api/documents`
- `GET /api/documents/{id}`
- `POST /api/documents/{id}/retry-ingestion`
- `POST /api/chat/query`
- `GET /api/chat/history`

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

- `admin@calisto.ai` / `password123`
- `member@calisto.ai` / `password123`
- `viewer@calisto.ai` / `password123`

## Architecture Overview

See:

- `/docs/ARCHITECTURE.md`
- `/docs/PORTS.md`
- `/docs/STYLEGUIDE.md`

## Roadmap

- Replace in-memory vector implementation with persistent FAISS index service
- Add pgvector provider implementation behind vector store interface
- Add SSO/SCIM integrations for enterprise identity workflows
- Add audit logs, tracing, and richer metrics dashboards
- Add document parsing for PDF/DOCX inputs and async ingestion jobs
