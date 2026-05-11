# Architecture

Callisto is a monorepo with a FastAPI backend, a React + Vite frontend, and a
relational database for system-of-record state. The retrieval layer is built
on a swappable embedding service so the demo runs with no external API keys
but can be upgraded to a real embedding provider without touching call sites.

## High-Level Components

- **Frontend** (`frontend/`) — React + Vite + Tailwind SPA for auth, document
  upload, chat, and admin dashboards.
- **Backend** (`backend/`) — FastAPI app with layered architecture
  (`routers/` → `services/` → `models/` / `db/`).
- **Database** — SQLite locally (default) or PostgreSQL via `DATABASE_URL`.
  Users, organizations, collections, documents, chunks, chunk embeddings,
  chat sessions/messages, and audit logs.
- **Vector layer** — Chunk embeddings are persisted in the `chunk_embeddings`
  table; an in-memory FAISS index is built lazily for fast cosine search.
  Hybrid retrieval blends vector, keyword, and metadata signals.

## Backend layering

| Layer | Responsibility |
|---|---|
| `routers/` | HTTP route handlers, request/response shaping, dependency wiring |
| `schemas/` | Pydantic request/response contracts |
| `services/` | Domain workflows: ingestion, embedding, retrieval, rerank, answer, audit, admin |
| `models/` | SQLAlchemy 2.0 ORM entities |
| `db/` | Engine/session/bootstrap and demo seed data |
| `core/` | Auth, JWT, RBAC dependencies, logging, metrics, rate limiting |

## RAG flow

```
1. Upload      POST /api/documents/upload
   └── DocumentService → IngestionService.chunk_document()
        ├── semantic-unit splitter (paragraph → sentence)
        └── sliding-window fallback for oversize units
   └── EmbeddingService.embed_text() per chunk
   └── EmbeddingIndexService.upsert_chunk_embedding() persists vector
   └── In-memory FAISS index updated

2. Query       POST /api/chat/query
   └── ChatService.query()
        ├── QueryRewriteService (light query normalization)
        ├── RetrievalService.retrieve()
        │     ├── embedding_index_service.search() (cosine)
        │     ├── keyword_search() (term-overlap + metadata)
        │     └── RerankService.rerank() (weighted blend)
        ├── LLMService.generate_grounded_answer()
        │     └── HeuristicGroundedLLM composes a cited answer
        └── AuditService records the request + latency breakdown
   └── Response: answer, citations, confidence, latency_breakdown_ms
```

## Multi-tenancy & RBAC

Every domain table that holds tenant data has an `organization_id` column.
Each service query filters by the requesting user's `organization_id` so a
user cannot read documents from another organization even if they guess an
ID. Role checks (`admin`, `member`) are enforced via FastAPI dependencies
(`require_roles(...)`).

The `audit_log` table records ingestion, retrieval, and admin actions for
compliance review.

## What is real vs heuristic

This is a portfolio project, so two pieces are intentionally simple and are
swap-in points for a production deployment:

| Component | Current implementation | Production swap |
|---|---|---|
| Embedding | Deterministic 32-dim hash of the chunk text | Sentence Transformers / OpenAI / Cohere embeddings |
| LLM answer | Heuristic that composes an answer from the top citations | OpenAI / Anthropic / local model via a new `LLMService` provider |
| Vector index | In-memory FAISS (rebuilt on startup) | pgvector or a managed vector DB |
| Reranker | Term-overlap + metadata-weighted blend | Cross-encoder (e.g. `cross-encoder/ms-marco-MiniLM-L-6-v2`) |

The interfaces (`EmbeddingService`, `LLMService`, `VectorStore`, `RerankService`)
were designed so each can be replaced without touching the routers.
