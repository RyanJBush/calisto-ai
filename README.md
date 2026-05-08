![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat&logo=typescript&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![CI](https://github.com/RyanJBush/Enterprise-RAG-knowledge-platform/actions/workflows/ci.yml/badge.svg)

# Calisto AI

> An enterprise Retrieval-Augmented Generation (RAG) knowledge platform with hybrid retrieval, citation-aware answers, multi-tenant RBAC, and a production-ready document ingestion pipeline — built to explore what it takes to make LLM-powered Q&A trustworthy and auditable at enterprise scale.

---

## 🎯 What I Built & Why

RAG systems are easy to demo but hard to trust. I built Calisto AI to solve the reliability and accountability gaps that most RAG demos ignore:

- **Hybrid retrieval** — vector similarity search + BM25-style keyword search blended with reranking. Pure vector search misses exact-match queries; hybrid retrieval handles both
- **Citation-aware answers** — every answer is traced back to specific source chunks with relevance scores and highlighted evidence — no black-box generation
- **Multi-tenant RBAC** — organizations, users, documents, and chat sessions are fully tenant-isolated with Admin/Member/Viewer roles, reflecting real enterprise deployment requirements
- **Background ingestion with retry** — document processing runs as tracked background jobs with status polling and retry logic, so large document sets don’t block the UI

---

## 📷 Features

- **Hybrid retrieval** — vector + BM25 blending with configurable top-k and reranking
- **Semantic chunking** — paragraph + sentence boundary chunking with configurable size and overlap
- **Citation-aware answers** — every response traces back to source chunks with confidence scores and highlighted evidence
- **Document ingestion pipeline** — PDF, TXT, Markdown; deduplication, PII redaction, chunk preview before indexing
- **Background ingestion jobs** — async processing with status tracking and retry logic
- **Multi-tenant RBAC** — Admin, Member, Viewer roles with full tenant isolation
- **Admin analytics dashboard** — query volume, avg latency, top documents, ingestion breakdown, audit logs
- **Seeded demo dataset** — 5 enterprise knowledge documents pre-chunked and indexed for instant querying
- **React SaaS UI** — confidence badges, source preview panel, citation cards, latency breakdown

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI + SQLAlchemy + PostgreSQL |
| Retrieval | Vector similarity + BM25-style keyword search with reranking |
| Auth | JWT with RBAC (3 roles, multi-tenant) |
| Frontend | React + Vite + Tailwind CSS |
| Infra | Docker Compose + GitHub Actions CI |

---

## 🚀 Quick Start

### Prerequisites
- Docker + Docker Compose
- Python 3.11+
- Node.js 20+

### Local Development
```bash
make bootstrap
cp backend/.env.example backend/.env
make db-upgrade
make init                   # seeds demo documents
make run-backend            # http://localhost:8000
make run-frontend           # http://localhost:5173
```

### Fast Demo (< 2 minutes)
1. Start backend and frontend as above
2. Open `http://localhost:5173` and log in as `admin@calisto.ai` / `password123`
3. Navigate to **Chat** and try one of the example queries:
   - *"What is the leave policy?"*
   - *"What is the escalation window for P1 incidents?"*
   - *"What is the data retention period for customer documents?"*
4. Inspect the **confidence badge**, **citation cards**, **source preview panel**, and **latency breakdown**
5. Go to **Documents** to upload a new file and preview chunks before indexing

### Docker Compose
```bash
docker compose up --build
```

### Quality Checks
```bash
make lint
make test
make db-upgrade   # apply migrations
```

---

## 🗂️ Repository Structure

```
backend/    FastAPI API, RAG services, hybrid retrieval, ingestion pipeline, RBAC, tests
frontend/   React SaaS UI (chat, documents, admin dashboard)
docs/       Architecture, ports, style guide
```

---

## 👤 Demo Credentials

| Email | Password | Role |
|---|---|---|
| `admin@calisto.ai` | `password123` | Admin |
| `member@calisto.ai` | `password123` | Member |
| `viewer@calisto.ai` | `password123` | Viewer |

---

## 📖 Seeded Demo Documents

| Document | Content |
|---|---|
| Employee Handbook | Leave policy, remote work, expenses, performance reviews, code of conduct |
| Security Operations Guide | P1–P4 incident levels, escalation, vulnerability management, access control |
| Support SLA | Response/resolution targets by plan, escalation, SLA credits |
| Engineering Onboarding | Dev workflow, tech stack, deployment, on-call rotation |
| Data Retention Policy | Retention periods, backup, GDPR/CCPA compliance |

---

## 📝 Key Learnings

- Hybrid retrieval (vector + keyword) meaningfully outperforms pure vector search on exact-match queries — the BM25 component catches terminology that embeddings can miss
- Citation traceability is what separates a trustworthy enterprise RAG system from a plausible-sounding one; every answer must be auditable back to a source chunk
- Multi-tenant isolation requires careful data model design upfront — retrofitting RBAC and tenant boundaries into an existing schema is much harder than building them in from the start

---

## 🛣️ Roadmap

- Replace in-memory vector implementation with persistent FAISS index service
- Add pgvector provider behind the vector store interface
- Add SSO/SCIM integrations for enterprise identity workflows
- Add OpenAI / Anthropic LLM provider behind the existing `LLMService` interface

---

## 📄 License

MIT
