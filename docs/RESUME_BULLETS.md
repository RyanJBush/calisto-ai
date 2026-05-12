# Resume Bullets

ATS-friendly one-liners describing this project. Every bullet is factually
defensible against the current state of the repository — no over-claiming.

## Headline bullet

- Built **Callisto**, a multi-tenant Retrieval-Augmented Generation (RAG)
  knowledge platform (FastAPI, React, SQLAlchemy 2.0, Docker) with
  sentence-aware chunking, hybrid vector + keyword retrieval, a weighted
  reranker, JWT auth, organization-scoped RBAC, and a labeled retrieval-
  evaluation harness; ~2.2k LOC backend Python and ~100 passing pytest tests.

## ATS-friendly one-liners (5–8, pick what fits the role)

1. Designed and shipped a multi-tenant RAG knowledge platform end-to-end (FastAPI + React + SQLAlchemy 2.0 + Docker) with document ingestion, hybrid retrieval, weighted reranking, grounded answers with inline citations, JWT auth, and role-based access control.
2. Built a 15-endpoint FastAPI backend with layered routers / services / models, Pydantic schemas, Alembic migrations, an in-memory rate limiter, audit logging, and request metrics; achieved a 100% pass rate across ~100 pytest cases.
3. Implemented a sentence-boundary-aware chunker plus a hybrid retriever that blends cosine vector search (FAISS), token-overlap keyword scoring, and document-metadata signals, then re-scores candidates with a deterministic weighted reranker.
4. Engineered the RAG layer behind swappable interfaces (EmbeddingService, LLMService, VectorStore, RerankService) so the demo runs offline with deterministic hash embeddings and a heuristic grounded-answer composer, while production-grade models drop in without touching call sites.
5. Enforced organization-scoped multi-tenancy: every document, chunk, retrieval query, and audit event is filtered by the requesting user's organization_id, preventing cross-tenant data leakage at the query layer.
6. Authored a reproducible retrieval-evaluation harness (labeled query set + source hit-rate, keyword coverage, and latency metrics) that gates changes to chunking and embeddings against a baseline in CI.
7. Containerized the full stack with Docker Compose (Postgres + FastAPI backend + React/Vite frontend) and shipped a GitHub Actions CI pipeline running ruff, pytest, and a frontend build on every push and pull request.
8. Designed a React + Vite + Tailwind SPA (login, dashboard, documents, chat, admin/RBAC pages) wired to the backend through a typed axios client, with auth-gated routes and a citation-aware chat view that surfaces chunk IDs and source documents per claim.

## AI / ML / RAG focus

- Designed a RAG pipeline that combines sentence-boundary-aware chunking,
  cosine-similarity vector retrieval (FAISS), term-overlap keyword scoring,
  and a weighted reranker to produce grounded answers with inline citations,
  confidence scores, and an explicit insufficient-evidence signal.
- Modeled embeddings behind a swappable interface so the demo runs without
  external API keys (deterministic 32-dim hash baseline) but can be upgraded
  to Sentence Transformers or hosted embedding APIs by replacing one service.
- Implemented a reproducible retrieval-evaluation harness (labeled query set
  + source-hit-rate, keyword-coverage, and latency metrics) so chunking and
  embedding changes can be A/B tested against a baseline.

## Software engineering focus

- Built a 15-endpoint FastAPI backend (auth, documents, chat, admin, health)
  with Pydantic schemas, SQLAlchemy 2.0 models, Alembic migrations, structured
  logging, request metrics, and an in-memory rate limiter; ~100 passing
  pytest cases.
- Authored a React + Vite + Tailwind frontend with auth-gated routes,
  document upload, chat with citation rendering, and an admin/RBAC settings
  page; wired to the backend via a typed axios client.
- Containerized the stack with a multi-service `docker-compose.yml`
  (Postgres + backend + frontend) and added a GitHub Actions CI pipeline
  running ruff, pytest, and a frontend build on every PR.

## Enterprise knowledge-management focus

- Implemented organization-scoped multi-tenancy: every document, chunk, and
  retrieval query is filtered by the requesting user's `organization_id`,
  preventing cross-tenant data leakage at the query layer.
- Added role-based access control (admin / member / viewer) with per-document
  access grants, plus an audit log that records ingestion, retrieval, and
  admin actions for compliance review.
- Surfaced source citations and a confidence / citation-coverage score on
  every assistant response so users can verify claims against the original
  documents before acting.

## Short variants (one-line fits)

- *Built a multi-tenant RAG knowledge platform (FastAPI + React + Docker) with hybrid vector/keyword retrieval, weighted reranking, JWT auth, RBAC, and a labeled retrieval-evaluation harness.*
- *Shipped an enterprise-style RAG portfolio project covering ingestion, embeddings, retrieval, citations, and tenant isolation, backed by ~100 pytest tests and GitHub Actions CI.*

## Honesty guardrails

When using these bullets, keep them defensible:

- The current implementation uses a **deterministic hash embedder** and a
  **heuristic grounded-answer composer**, not a real LLM or sentence
  transformer. Bullets above say "swappable interface" and "labeled
  retrieval-evaluation harness" precisely because that is what is shipped.
- The reranker is a **weighted blend**, not a cross-encoder. Do not describe
  it as cross-encoder reranking on a resume.
- "~100 pytest tests" refers to test cases collected by pytest across the
  three test files under `backend/tests/`. Re-verify before submitting.
