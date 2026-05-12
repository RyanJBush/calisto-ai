# Architecture — Callisto

## Plain-English summary

Callisto is a local demo of an enterprise-style RAG platform architecture. The important word is **architecture**: this repo focuses on system structure, isolation boundaries, and retrieval workflow more than on model quality.

## System components

- **Frontend (`frontend/`)**: React + Vite UI for login, document upload, chat, and admin views.
- **Backend (`backend/`)**: FastAPI app split into routers, services, schemas, and models.
- **Database**: SQLite by default (PostgreSQL optional via `DATABASE_URL`).
- **Vector retrieval layer**: Embeddings persisted in DB; in-memory FAISS index used at runtime.

## Request flow

1. User uploads a document.
2. Ingestion service chunks content.
3. Embedding service creates deterministic hash embeddings per chunk.
4. Chunks + embeddings are persisted and indexed.
5. Query endpoint retrieves candidates (vector + keyword signals).
6. Weighted reranking adjusts candidate order.
7. Answer service assembles a grounded heuristic response with citations.

## Honesty section: model behavior

### LLM generation
There is **no real external LLM text generation in the default flow**. The answer composer is heuristic and citation-grounded.

### Embeddings
Embeddings are **deterministic hash embeddings**. This is good for reproducibility and local setup, but limited for semantic nuance.

### Reranking
Reranking uses **weighted reranking** (feature blending). It is **not cross-encoder reranking** unless you add a real cross-encoder implementation.

## Why these defaults exist

- no external API dependency
- no API keys required
- deterministic behavior for demos/tests
- easier debugging and code review

## Swap-in points for production-like upgrades

- `EmbeddingService`: replace hash embeddings with Sentence Transformers or hosted embedding APIs.
- `LLMService`: add provider-backed generation (OpenAI/Anthropic/local model).
- `RerankService`: replace weighted reranking with a true cross-encoder reranker.
- Vector layer: persist index or move to pgvector / managed vector DB.

## Security and tenancy posture (demo scope)

- JWT-based auth and RBAC are implemented.
- Organization scoping is enforced at query/service level.
- This is still a portfolio demo, not a hardened production deployment.

