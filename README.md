# Callisto — Enterprise RAG Knowledge Platform

Callisto is a **local portfolio demo** that shows how a RAG-style system can be wired end to end: upload docs, chunk text, create embeddings, retrieve relevant chunks, rerank results, and return a cited answer.

This repository is intentionally honest about what is implemented today:

- **No real LLM generation by default.** Answers are composed with a deterministic heuristic from retrieved chunks.
- **Embeddings are deterministic hash embeddings.** They are useful for exercising architecture, not for state-of-the-art semantic search quality.
- **Reranking is weighted reranking.** It is not cross-encoder reranking in the current implementation.

If you want to evaluate engineering quality (API shape, service boundaries, data model, multi-tenant filtering, auth/RBAC, testability), this project is built for that.

---

## What this project is (and is not)

**Is:**
- A readable RAG architecture demo you can run locally.
- A backend/frontend system with realistic seams for swapping in real model providers.
- A portfolio artifact focused on clear tradeoffs and reproducible behavior.

**Is not:**
- A production deployment.
- A benchmark-leading retrieval stack.
- A hosted SaaS product.

---

## Quick start

```bash
git clone https://github.com/RyanJBush/Enterprise-RAG-knowledge-platform.git
cd Enterprise-RAG-knowledge-platform
docker compose up --build
```

Then open:
- API docs: `http://localhost:8000/docs`
- Frontend: `http://localhost:5173`

Seeded users:
- `admin@calisto.ai` / `password123`
- `member@calisto.ai` / `password123`
- `viewer@calisto.ai` / `password123`

---

## Technical reality check

| Area | Current implementation |
|---|---|
| Answer generation | Heuristic grounded composer (`answer_mode: grounded_heuristic`) |
| Embeddings | Deterministic 32-d hash embeddings |
| Reranking | Weighted reranking over retrieval features |
| Vector index | In-memory FAISS |
| Isolation | Organization-scoped filtering in service/query layer |

These defaults are deliberate: they keep the project offline, deterministic, and easy to inspect.

---

## Why this is still valuable

Even with heuristic/default ML components, this repo demonstrates core RAG engineering skills:

- ingestion/chunking pipelines
- retriever orchestration
- explicit service interfaces (`EmbeddingService`, `LLMService`, `RerankService`)
- API contracts and validation
- auth + RBAC
- auditability and metrics hooks
- regression-friendly evaluation scripts

That is often the hardest part to get right before plugging in expensive model APIs.

---

## Documentation map

- Architecture: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- API: [`docs/API.md`](docs/API.md)
- Demo walkthrough: [`docs/DEMO_RUNBOOK.md`](docs/DEMO_RUNBOOK.md)
- Resume bullets: [`docs/RESUME_BULLETS.md`](docs/RESUME_BULLETS.md)
- Screenshots guide: [`docs/screenshots/README.md`](docs/screenshots/README.md)

