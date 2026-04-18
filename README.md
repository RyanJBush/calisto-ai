# Calisto AI

Calisto AI is a production-style, enterprise-inspired RAG (Retrieval-Augmented Generation) knowledge platform scaffolded as a monorepo. This MVP foundation is designed for rapid iteration while signaling strong software engineering fundamentals for portfolio and recruiter review.

## Overview

Calisto AI aims to provide secure, citation-based Q&A over internal knowledge, with future-ready multi-tenant architecture and clear operational boundaries between API, UI, data, and search layers.

## Core features (MVP foundation)

- FastAPI backend with modular architecture (`routers`, `services`, `schemas`, `models`)
- React + Vite + Tailwind frontend with authenticated app shell layout
- PostgreSQL integration via SQLAlchemy
- FAISS-ready service layer placeholder for vector indexing and retrieval
- JWT + RBAC auth scaffolding for enterprise access control patterns
- Dockerized local development and service orchestration
- CI workflow with backend and frontend quality gates
- Engineering standards: Ruff, Pytest, ESLint, Prettier

## Architecture summary

- **Frontend (`frontend/`)**: React SPA for dashboard, documents, chat, and auth.
- **Backend (`backend/`)**: FastAPI API for health, auth, documents, and chat domains.
- **Database (`postgres`)**: stores tenants, users, documents, metadata, and audit-ready entities.
- **Vector layer (FAISS placeholder)**: planned for semantic retrieval in the chat workflow.
- **Infrastructure**: Docker Compose for local runtime, Makefile for standard task execution, GitHub Actions for CI.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) and [`docs/PORTS.md`](docs/PORTS.md) for details.

## Local setup

### Prerequisites

- Docker + Docker Compose
- Python 3.11+
- Node.js 20+
- Make

### Bootstrap

```bash
make bootstrap
```

### Run services

```bash
# API (http://localhost:8000)
make run-backend

# Web app (http://localhost:5173)
make run-frontend

# Optional: full local stack with DB
make up
```

### Quality checks

```bash
make lint
make test
```

## Repository layout

```text
calisto-ai/
  backend/
  frontend/
  docs/
  README.md
  LICENSE
  CONTRIBUTING.md
  .gitignore
  .editorconfig
  Makefile
  docker-compose.yml
```

## Roadmap (Phase 2+)

1. Implement tenant-aware persistence models and Alembic migrations.
2. Add secure upload pipeline + chunking/embedding jobs.
3. Implement FAISS index lifecycle and retrieval ranking.
4. Wire LLM provider integration with citation grounding.
5. Add JWT refresh flow, role enforcement middleware, and audit events.
6. Build document processing observability and production deployment manifests.

## Why this project stands out

- Enterprise patterns from day one (modular boundaries, quality checks, CI/CD)
- Security-first architecture intent (JWT, RBAC, multi-tenant framing)
- Practical AI product direction (document ingestion + citation QA)
- Professional repository hygiene recruiters expect
