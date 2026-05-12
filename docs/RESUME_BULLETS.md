# Resume Bullets

ATS-friendly one-liners describing this project. Pick the variants that match
the role you are applying to. Each bullet has been written to be factually
defensible against the current state of the repository — do not over-claim.

## Headline bullet

- Built **Callisto**, an enterprise-style Retrieval-Augmented Generation (RAG)
  platform (FastAPI, React, SQLAlchemy, Docker) with document ingestion,
  hybrid vector + keyword retrieval, reranking, JWT auth, and tenant-scoped
  RBAC; ~2.2k LOC of backend Python and ~100 passing pytest tests.

## AI / ML / RAG focus

- Designed a RAG pipeline that combines sentence-boundary-aware chunking,
  cosine-similarity vector retrieval, BM25-style keyword scoring, and a
  weighted reranker to produce grounded answers with inline source citations.
- Implemented a reproducible retrieval-evaluation harness (labeled query set
  + source-hit-rate, keyword-coverage, and latency metrics) so changes to
  chunking or embeddings can be A/B tested against a baseline.
- Modeled embeddings behind a swappable interface so the demo runs without
  external API keys (deterministic hash baseline) but can be upgraded to
  Sentence Transformers or OpenAI embeddings by changing a single service.

## Software engineering focus

- Built a 15-endpoint FastAPI backend (auth, documents, chat, admin, health)
  with Pydantic schemas, SQLAlchemy 2.0 models, Alembic migrations, and an
  in-memory rate limiter; achieved 100% test pass rate across ~100 pytest cases.
- Authored a React + Vite + Tailwind frontend with auth-gated routes,
  document upload, chat, and admin pages; wired it to the backend through a
  typed axios client.
- Containerized the stack with a multi-service `docker-compose.yml`
  (Postgres + backend + frontend) and added a GitHub Actions CI pipeline
  running ruff, pytest, and a frontend build on every PR.

## Enterprise knowledge-management focus

- Implemented organization-scoped multi-tenancy: every document, chunk, and
  retrieval query is filtered by the requesting user's `organization_id`,
  preventing cross-tenant data leakage at the query layer.
- Added role-based access control (admin / member) with per-document access
  grants, plus an audit log that records ingestion, retrieval, and admin
  actions for compliance review.
- Surfaced source citations and a confidence / citation-coverage score on
  every assistant response so users can verify claims against the original
  documents before acting.

## Short variants (one-line fits)

- *Built a multi-tenant RAG knowledge platform (FastAPI + React + Docker) with hybrid vector/keyword retrieval, reranking, JWT auth, RBAC, and a labeled retrieval-evaluation harness.*
- *Shipped an enterprise-style RAG portfolio project covering ingestion, embeddings, retrieval, citations, and tenant isolation, backed by ~100 pytest tests and GitHub Actions CI.*
