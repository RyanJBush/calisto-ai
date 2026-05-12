# Demo Runbook (Honest Version)

Use this when presenting Callisto to a recruiter or hiring manager.

## 1) Start locally

```bash
docker compose up --build
```

Open:
- `http://localhost:5173` (UI)
- `http://localhost:8000/docs` (API docs)

## 2) Explain scope up front

Say this early:

> “This is a local portfolio demo of RAG architecture. Answers are heuristic, embeddings are deterministic hash embeddings, and reranking is weighted reranking. I can show exactly where to swap in production model providers.”

This prevents confusion and builds trust.

## 3) Login and upload

Login with `admin@calisto.ai / password123`.
Upload a sample document from `data/samples/`.

## 4) Run a query

Ask: “How many PTO days do employees get?”

Point out:
- citation list and chunk/source traceability
- `answer_mode: grounded_heuristic`
- latency breakdown fields

## 5) Show RBAC quickly

Login as `viewer@calisto.ai` and show admin route restriction (`403` on admin metrics).

## 6) Mention upgrade path

Show where to upgrade:
- embeddings (`EmbeddingService`)
- LLM generation (`LLMService`)
- reranking (`RerankService`)

## 7) One-line close

> “The point of this project is reliable RAG plumbing and truthful system boundaries, not pretending heuristic components are production AI.”

