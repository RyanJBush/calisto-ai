# Demo Runbook

A step-by-step script for walking a recruiter, hiring manager, or interviewer
through Callisto end-to-end in roughly five minutes. Everything below runs
locally with no API keys.

> **Scope.** Callisto is a local-demo portfolio project. There is no hosted
> instance, no real user data, and the answer generator is a deterministic
> heuristic — not a real LLM. The runbook is intentionally honest about what
> the demo is showing and where the production swap-in points are.

---

## 0. Prerequisites

- Docker + Docker Compose, **or** Python 3.11+ and Node 18+
- `curl` and `jq` for the API smoke tests (optional but recommended)

---

## 1. Bring the stack up

### Option A — Docker Compose (one command)

```bash
docker compose up --build
```

When the logs settle you should see:

```
backend   | Uvicorn running on http://0.0.0.0:8000
frontend  | Local:   http://localhost:5173/
```

### Option B — Local processes

```bash
./scripts/quickstart.sh
make run-backend     # terminal 1
make run-frontend    # terminal 2
```

The first start runs Alembic migrations and seeds three demo users plus a
small sample corpus.

---

## 2. Confirm the API is up

```bash
curl -s http://localhost:8000/health
# {"status":"ok"}
```

Then open **http://localhost:8000/docs** in a browser. You should see the
Swagger UI listing 15 endpoints across `auth`, `documents`, `chat`, `admin`,
and `health`.

---

## 3. Log in as the seeded admin

In the UI: open **http://localhost:5173**, choose **Login**, and use:

| Email | Password | Role |
|---|---|---|
| `admin@calisto.ai` | `password123` | admin |
| `member@calisto.ai` | `password123` | member |
| `viewer@calisto.ai` | `password123` | viewer |

Or from the CLI:

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@calisto.ai","password":"password123"}' \
  | jq -r .access_token)
echo "$TOKEN" | head -c 40 ; echo
```

> These are **local demo credentials.** Do not reuse them anywhere real, and
> change `JWT_SECRET` before any non-local use.

---

## 4. Upload a document

In the UI, open the **Documents** page and either upload one of the seeded
files from `data/samples/` or paste your own plain text.

From the CLI:

```bash
curl -s -X POST http://localhost:8000/api/documents/upload \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d @- <<'JSON'
{
  "title": "Employee Handbook",
  "source_name": "employee_handbook.txt",
  "content": "Employees accrue 15 days of paid time off per year. Meals are reimbursed up to $75 per day on approved travel."
}
JSON
```

The response confirms the document was chunked and indexed (chunk count,
ingestion latency, document ID).

---

## 5. Ask a grounded question

In the UI, open **Chat** and ask:

> *How many PTO days do employees get?*

You should see an answer that quotes the upload back with an inline citation
(document title + chunk ID + snippet), plus a confidence score and a
`latency_breakdown_ms`.

From the CLI:

```bash
curl -s -X POST http://localhost:8000/api/chat/query \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"query":"How many PTO days do employees get?","top_k":3,"grounded_mode":true}' \
  | jq
```

Expected shape:

```json
{
  "answer": "Based on the indexed knowledge base:\n\n[1] Employees accrue 15 days...",
  "answer_mode": "grounded_heuristic",
  "confidence_score": 0.7,
  "citation_coverage": 1.0,
  "insufficient_evidence": false,
  "citations": [
    { "document_title": "Employee Handbook", "chunk_id": 42, "retrieval_score": 0.81, "snippet": "..." }
  ],
  "latency_breakdown_ms": { "retrieve": 12, "rerank": 3, "generate": 1 }
}
```

What to point at:

- **`answer_mode: grounded_heuristic`** — the answer was composed from the
  top retrieved chunks by a deterministic heuristic. No external LLM is called.
- **`citations[]`** — every claim is traceable to a specific chunk. This is
  the "grounded" part of grounded answers.
- **`latency_breakdown_ms`** — retrieve / rerank / generate are measured
  independently so the bottleneck is visible.

---

## 6. Show multi-tenant isolation and RBAC

Log out and log back in as **`viewer@calisto.ai`** (or get a new token).

```bash
VIEWER_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"viewer@calisto.ai","password":"password123"}' \
  | jq -r .access_token)

# Viewer cannot read admin metrics
curl -s -o /dev/null -w "%{http_code}\n" \
  -H "Authorization: Bearer $VIEWER_TOKEN" \
  http://localhost:8000/api/admin/metrics
# 403
```

In the UI, the **Settings** page hides admin-only actions for the viewer
account. This is the RBAC layer (`require_roles(...)` FastAPI dependency).

Tenant isolation is enforced at the service layer: every query filters by
`organization_id`, so a user registered under a different organization cannot
see this organization's documents even if they guess an ID.

---

## 7. Run the retrieval-evaluation harness

```bash
python scripts/evaluate_retrieval.py
```

The script logs in as the seeded admin, uploads the three sample documents in
`data/samples/`, runs the 6 labeled queries in `data/samples/eval_set.json`,
and prints:

- **Source hit rate** — fraction of queries where an expected source document
  appears in the top-k retrieved chunks.
- **Keyword coverage** — fraction of expected keywords present in the
  concatenated retrieved chunks.
- **Mean retrieval latency (ms).**

The script exits non-zero if the source hit rate drops below the threshold
defined at the top of the file — useful as a regression gate when changing
chunking or embeddings.

See [EVALUATION.md](EVALUATION.md) for methodology and known limitations
(notably: the eval set is small and there is no LLM-as-judge step).

---

## 8. Run the test suite

```bash
make test            # ~100 pytest cases + frontend build
make lint            # ruff + eslint
```

The same jobs run on every push and PR via
[`.github/workflows/ci.yml`](../.github/workflows/ci.yml).

---

## 9. Talking points

When walking someone through this, the things worth pointing at:

1. **`HeuristicGroundedLLM` is honest.** The `answer_mode` field marks the
   response as heuristic. Swap in a real LLM by adding a provider to
   `app/services/llm_service.py` and flipping `LLM_PROVIDER`.
2. **Embeddings are a deterministic hash.** That keeps the demo offline and
   reproducible. The eval harness is the way to measure what a real embedder
   would gain.
3. **Reranker is a weighted blend, not a cross-encoder.** The weights live
   in `app/services/rerank_service.py` and are explicit (0.50 / 0.30 / 0.10 /
   0.10). Production swap is a real cross-encoder behind the same interface.
4. **Tenant isolation is at the query layer** — every service filters by
   `organization_id`. Production hardening would add Postgres row-level
   security policies on top.
5. **Audit log, rate limiter, metrics, RBAC, JWT, Alembic, CI** — the
   "boring" production pieces are all wired up.

---

## 10. Tear down

```bash
docker compose down -v       # remove containers + volumes
```

Or kill the local processes started by `make run-*`.
