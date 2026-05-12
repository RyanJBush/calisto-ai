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

This is a local-demo portfolio project, so four components are intentionally
simple and are designed as swap-in points for a production deployment. The
table below is the honest version — none of these call an external service in
the current implementation.

| Component | Current implementation | Where it lives | Production swap |
|---|---|---|---|
| Embedding | Deterministic 32-dim SHA-256 hash of the chunk text | `app/services/embedding_service.py` | Sentence Transformers (`all-MiniLM-L6-v2`) for local, or OpenAI / Cohere / Voyage hosted embeddings |
| LLM answer | `HeuristicGroundedLLM` — composes a structured, cited answer from the top retrieved chunks; no model call | `app/services/llm_service.py` | OpenAI / Anthropic / local model behind a new provider in `LLMService`, selected via `LLM_PROVIDER` |
| Vector index | In-memory FAISS, rebuilt on startup from `chunk_embeddings` | `app/services/embedding_index_service.py`, `app/services/vector_store.py` | `pgvector` or a managed vector DB; warm from a persisted snapshot |
| Reranker | **Weighted blend** of base score (0.50) + query-term coverage (0.30) + title boost (0.10) + metadata score (0.10). Not a neural cross-encoder. | `app/services/rerank_service.py` | A real cross-encoder such as `cross-encoder/ms-marco-MiniLM-L-6-v2`, or a hosted reranker (Cohere / Voyage) behind the same `RerankService` interface |

The interfaces (`EmbeddingService`, `LLMService`, `VectorStore`, `RerankService`)
are explicit seams: each can be replaced without touching the routers or the
chat service that orchestrates them.

## Honesty notes

- The phrase "cross-encoder reranking" is **not** used in the codebase or the
  recruiter-facing docs because no cross-encoder is invoked. The reranker is
  a deterministic weighted scoring function — easy to read, easy to unit test,
  and entirely sufficient for demonstrating where a real reranker would slot in.
- The `LLM_MODEL` env var is a label only; no external model is contacted. The
  `answer_mode` returned by `/api/chat/query` is `grounded_heuristic` precisely
  so callers cannot mistake it for a real generative answer.
- Embeddings are deterministic, which means semantic recall is limited. The
  hybrid retriever leans on keyword and metadata signals to compensate; the
  retrieval-evaluation harness in `scripts/evaluate_retrieval.py` measures
  this honestly.
