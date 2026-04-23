# Calisto AI Codebase Audit & Implementation Plan

## 1) Current State Summary

### What is already implemented
- Monorepo split into FastAPI backend and React/Vite frontend with Dockerfiles, root `docker-compose.yml`, `Makefile`, and CI workflow.
- Backend architecture is cleanly layered (`routers`, `schemas`, `services`, `models`, `db`, `core`) and includes:
  - JWT auth + role checks (`admin`, `member`, `viewer`)
  - Multi-tenant-ish models (organizations, users, docs, chunks, sessions/messages)
  - Document upload -> ingestion run -> chunking -> embedding -> vector indexing path
  - Retrieval blending vector + keyword + metadata, plus reranking
  - Citation-rich chat response payload (source preview + highlight ranges + confidence)
  - Admin analytics endpoints and audit logging
- Frontend includes routed app shell with key pages: Login, Dashboard, Documents, Chat, Settings.
- Backend tests exist and are broad for API + utility logic.

### What appears partially implemented
- “Enterprise RAG” is mostly an MVP simulation:
  - Deterministic hash embeddings (not model-based)
  - In-memory vector index (ephemeral per process)
  - Synchronous/in-process threadpool ingestion worker (not durable queue)
  - Answer generation is template-style, not LLM-backed
- Multi-tenant support is “tenant-aware data model” but single-org seeded and lacks tenant admin lifecycle.
- Security is baseline only (JWT + role gates + simple sanitizer/redaction), without enterprise hardening.
- UX is coherent but mostly functional, not highly polished.

### What is missing
- DB migrations (Alembic) and schema versioning.
- Production-grade worker orchestration and job persistence semantics.
- Persistent vector store (pgvector/managed vector DB) and re-indexing strategy.
- Real file ingestion/parsing (PDF, DOCX, HTML, connectors).
- LLM answering + model/provider config abstraction.
- Strong observability (structured metrics/traces), alerts, and SLO framing.
- Comprehensive frontend tests and e2e coverage.
- Deployment-ready production docs and environment matrix.

### What is broken or risky
- Backend test suite currently fails at startup due to passlib/bcrypt backend incompatibility in this environment; password hashing fails before seeded auth works.
- DB initialization uses `create_all` only; no migrations means risky schema evolution.
- In-memory vector index is empty across restarts and not rebuilt from DB on boot.
- Upload API only supports raw text payloads, no real file upload transport.
- Viewer access control depends on explicit grants, but no UI flow exists for grant/revoke admin operations.

### Whether the app appears runnable
- **Frontend build:** yes (build succeeds).
- **Backend/API runtime:** likely runnable in ideal dependency setup, but currently **not reliably runnable** due to bcrypt/passlib mismatch causing startup failure in tests.
- **End-to-end demo:** partially runnable conceptually, but not production-credible yet.

## 2) Completion Gap Analysis

### Backend
- Replace deprecated startup event pattern with lifespan.
- Add migration framework and initial migration set.
- Add robust error handling + typed domain exceptions.
- Decouple ingestion worker from API process.

### Frontend
- Missing admin controls for access grants, ingestion monitoring depth, and richer document metadata workflows.
- No loading skeletons, minimal empty/error states, limited interaction polish.
- Chat UX lacks streaming tokens, copy/share/export, and richer citation navigation.

### Database
- No Alembic migrations.
- No indexes tuned for query hotspots (beyond basic ids/content hash).
- No retention/data lifecycle strategy.

### Auth/Security
- Password hashing stack dependency mismatch (critical run blocker).
- Missing refresh tokens/session revocation/rotation.
- No CSRF strategy (if cookies used later), no brute-force defenses beyond coarse rate limit.
- No secrets management guidance for production.

### AI/RAG logic
- Embeddings are placeholder deterministic hashes.
- Answer generation is synthetic template output.
- No grounding guardrails beyond a heuristic confidence threshold.
- No model/provider abstraction for LLM + embedding backends.

### Ingestion pipeline
- Text-only ingestion; no parser abstraction for files/connectors.
- In-process thread pool jobs are not durable/resumable across crashes.
- No user-visible progress states beyond basic run statuses.

### APIs/Integrations
- Missing integration endpoints for external data sources (Confluence/Google Drive/Notion/S3/SharePoint).
- No webhooks for ingestion completion or errors.
- No API versioning strategy.

### Testing
- Backend tests exist but currently failing due to hashing backend issue.
- No frontend unit tests.
- No e2e tests (Playwright/Cypress).
- No load/reliability tests for ingestion and retrieval.

### Deployment/DevOps
- Docker Compose exists but no production deployment manifests (k8s/terraform/etc.).
- CI only does lint/backend tests/frontend build; no security scans or integration smoke tests.
- No release/versioning/changelog process.

### Documentation
- Good starter docs, but lacks production setup, architecture decisions (ADR), troubleshooting matrix, and demo script.

### UI/UX/Aesthetic polish
- Visual baseline is clean but generic.
- Limited visual hierarchy, no advanced information design for analytics/citations.
- Missing microinteractions and polished onboarding/demo cues.

### Demo-readiness
- Needs deterministic seed dataset beyond users.
- Needs scripted “happy path” scenario with realistic docs/questions.
- Needs stable local run instructions that work on fresh machine.

## 3) Recommended Final Scope (Ambitious but Achievable)

A strong portfolio-ready v1.0 should include:
1. **Reliable local dev + demo startup** (one command, deterministic seed, passing key tests).
2. **Credible RAG workflow**:
   - real embeddings (e.g., OpenAI or local sentence-transformers fallback),
   - persistent vector backend (pgvector),
   - retriever with metadata filters + rerank,
   - citation previews with highlight ranges.
3. **Practical ingestion**:
   - text + PDF ingestion,
   - background worker with retries and job status endpoint/UI.
4. **Enterprise-ish product surface**:
   - role-based auth,
   - workspace/org context,
   - admin analytics and audit trail.
5. **Polished UX**:
   - modern dashboard,
   - great chat+sources interaction,
   - robust states (loading/empty/error/success).
6. **Portfolio credibility**:
   - architecture docs, tradeoff notes, seed data story, screenshots/GIF, test coverage, CI green.

## 4) Phased Implementation Roadmap

### Phase 1 — Make app reliably runnable
**Objective**: Eliminate startup blockers and make fresh-clone setup deterministic.

**Likely files/folders**
- `backend/app/core/security.py`
- `backend/requirements.txt`, `backend/pyproject.toml`
- `backend/app/main.py`, `backend/app/db/*`
- `README.md`, `Makefile`, `docker-compose.yml`

**Concrete tasks**
- Fix password hashing dependency compatibility (pin compatible `bcrypt` or switch hash scheme config).
- Replace deprecated startup hook with lifespan bootstrapping.
- Add `.env.example` with required vars + defaults.
- Add “first run” script (`make init`) to bootstrap DB + seed data.
- Validate backend smoke tests and frontend build locally.

**Dependencies/blockers**
- Python package compatibility and lockfile consistency.

**Success criteria**
- `make bootstrap`, backend start, frontend start, login works using seeded users.
- Key API smoke path works end-to-end.

### Phase 2 — Data integrity + persistent retrieval core
**Objective**: Move from in-memory MVP to credible persistent RAG foundation.

**Likely files/folders**
- `backend/app/models/*`
- new `backend/alembic/*`
- `backend/app/services/vector_store.py`
- `backend/app/services/retrieval_service.py`
- `docker-compose.yml`

**Concrete tasks**
- Introduce Alembic migrations and initial migration baseline.
- Add pgvector-based implementation behind `VectorStore` interface.
- Add startup reindex/consistency check command.
- Tune retrieval indexes and SQL query performance.

**Dependencies/blockers**
- Postgres extension availability (`vector`).

**Success criteria**
- Retrieval persists across restarts.
- Migration workflow (`upgrade`, `downgrade`) works.

### Phase 3 — Complete ingestion and document workflows
**Objective**: Deliver realistic ingestion with traceable job lifecycle.

**Likely files/folders**
- `backend/app/services/ingestion_*`
- `backend/app/routers/documents.py`
- `frontend/src/pages/DocumentsPage.jsx`
- `frontend/src/services/api.js`

**Concrete tasks**
- Add multipart file upload endpoint + parser abstraction.
- Implement PDF text extraction path and validation.
- Introduce durable queue worker (RQ/Celery/Arq) with retries/backoff.
- Expose ingestion job details and progress in UI (queued/processing/completed/failed + errors).

**Dependencies/blockers**
- Worker runtime (Redis broker if needed).

**Success criteria**
- Upload PDF/text from UI and see reliable async ingestion completion.

### Phase 4 — Improve answer quality, citations, and trust UX
**Objective**: Make chat technically credible and demo-compelling.

**Likely files/folders**
- `backend/app/services/answer_service.py`
- `backend/app/services/embedding_service.py`
- `backend/app/services/retrieval_service.py`
- `frontend/src/pages/ChatPage.jsx`

**Concrete tasks**
- Add provider abstraction for LLM generation + embeddings (env-driven).
- Add grounded answer synthesis with source-constrained prompting.
- Improve citation coverage metrics and explanation badges.
- Add source panel UX: jump-to-highlight, relevance sorting, doc metadata chips.

**Dependencies/blockers**
- API keys/model availability.

**Success criteria**
- Answers are visibly grounded, citations clear, and trust indicators intuitive.

### Phase 5 — Admin/workspace polish + security hardening
**Objective**: Raise enterprise realism.

**Likely files/folders**
- `backend/app/routers/admin.py`, `services/admin_service.py`
- `backend/app/core/*`
- `frontend/src/pages/DashboardPage.jsx`, `SettingsPage.jsx`

**Concrete tasks**
- Add workspace/org settings page with tenant metadata.
- Add viewer access grant/revoke UI.
- Add auth hardening: token expiration UX, optional refresh flow, stronger rate limit policy.
- Improve audit detail and filtering.

**Dependencies/blockers**
- UX design decisions on role boundaries.

**Success criteria**
- Admin can operationally manage documents, access, and basic governance from UI.

### Phase 6 — Testing, docs, deployability, and demo prep
**Objective**: Make portfolio-ready and recruiter-impressive.

**Likely files/folders**
- `backend/tests/*`, new `frontend/src/**/*.test.*`, new e2e folder
- `.github/workflows/ci.yml`
- `README.md`, `docs/*`

**Concrete tasks**
- Add frontend unit tests + e2e smoke tests.
- Add CI matrix with backend+frontend+integration test jobs.
- Write complete runbook, troubleshooting, architecture decision notes, demo script.
- Add seeded demo corpus and scripted query scenarios.

**Dependencies/blockers**
- Stable fixtures and deterministic ingestion outputs.

**Success criteria**
- CI green, docs complete, demo can be run by third party from fresh clone.

## 5) Aesthetic / UX Improvements (High-impact, realistic)

1. **Layout + Navigation**
   - Add workspace switcher/org badge in topbar.
   - Add breadcrumb + page description patterns.
   - Refine spacing scale/typography and card hierarchy.

2. **Chat UX**
   - Two-pane layout with sticky citations panel.
   - Streaming response indicator + cancel/regenerate actions.
   - Prompt suggestions and quick filters (collection/document chips).

3. **Source Preview Panel**
   - Document title/source/version header.
   - Expandable context window around highlighted terms.
   - “Open full document” deep-link drawer.

4. **Document Upload + Status**
   - Drag-and-drop zone, file type badges, size validation.
   - Real-time ingestion status chips + retry action for failed runs.
   - Upload history table with sort/filter.

5. **Loading / Empty / Error States**
   - Skeleton placeholders on dashboard and chat history.
   - Empty states with CTA (“Upload your first doc”).
   - Inline retry/error callouts for API failures.

6. **Admin Dashboard polish**
   - Mini trend charts (queries/day, ingestion success rate).
   - KPI cards with deltas and tooltips.
   - Filterable audit trail with actor/action/resource columns.

7. **Demo friendliness**
   - “Sample questions” panel seeded from uploaded docs.
   - One-click “Load demo dataset” action.
   - “Tour mode” hints on first login.

## 6) Runnable / Usable Checklist

### Environment setup
- Python 3.11+, Node 20+, Docker optional.
- Install backend/frontend dependencies via `make bootstrap`.

### Required secrets/env vars
- `DATABASE_URL`
- `JWT_SECRET`
- `JWT_ALGORITHM` (optional override)
- `JWT_EXP_MINUTES` (optional override)
- `CORS_ORIGINS`
- (future) embedding/LLM provider keys

### Database setup
- Current: `Base.metadata.create_all` at startup.
- Target: Alembic migrations + explicit upgrade command.

### Seed/demo data
- Existing: demo org + 3 users seeded at startup.
- Needed: realistic demo documents and collections for showcase.

### Background workers
- Current: in-process threadpool ingestion.
- Target: dedicated worker service + broker + durable jobs.

### Vector store setup
- Current: in-memory FAISS/numpy fallback.
- Target: persistent pgvector (or managed vector DB) and reindex command.

### Package dependencies
- Resolve passlib/bcrypt compatibility issue first.
- Pin tested versions and document lock strategy.

### Startup commands
- Local API: `make run-backend`
- Local UI: `make run-frontend`
- Full stack: `docker compose up --build`

### Test commands
- `make lint`
- `make test`
- (target) e2e smoke tests

### Common failure points
- bcrypt/passlib mismatch causing auth seed failure.
- Missing/invalid `JWT_SECRET` in production setups.
- Vector state reset on restart (current in-memory behavior).
- Async ingestion race conditions in tests/demo timing.

## 7) Highest-ROI Improvements

1. **Fix run reliability + migration workflow**
   - Immediate credibility gain: “it runs on first try.”
2. **Persistent vector retrieval + real embeddings**
   - Biggest technical credibility multiplier for RAG.
3. **Polished chat citations UX**
   - Most visible recruiter wow-factor during demo.
4. **PDF ingestion + ingestion monitoring UI**
   - Product realism and enterprise readiness.
5. **End-to-end demo dataset + script + screenshots**
   - Converts engineering work into portfolio impact.

## 8) Clarifying Questions (Non-blocking)

Assumptions made for planning:
- Priority is portfolio-quality local deployment first, then cloud deployment.
- We can introduce one background dependency (e.g., Redis) if needed.
- We can use external model APIs in demo mode with fallback to local deterministic behavior.

Questions to confirm later (not blocking Phase 1):
1. Preferred primary LLM/embedding provider for portfolio demo (OpenAI vs local OSS model)?
2. Should final deploy target be single-node Docker Compose, or include cloud IaC reference?
3. Is SSO (OIDC/SAML) expected in final scope, or should JWT RBAC remain primary for v1?

---

## Executive Summary
Calisto AI has a solid scaffold and coherent MVP architecture but is not yet portfolio-complete. The biggest immediate blocker is runtime reliability (bcrypt/passlib startup failures), followed by persistence gaps (migrations + durable vector retrieval + worker durability). The fastest path to recruiter-impressive quality is: stabilize run experience, harden core RAG pipeline, then polish citations-centric UX and demo packaging.

## Recommended Implementation Order
1. Phase 1 (run reliability and setup hardening)
2. Phase 2 (DB migrations + persistent retrieval)
3. Phase 3 (real ingestion workflows + async durability)
4. Phase 4 (answer quality + trust UX)
5. Phase 5 (admin/security polish)
6. Phase 6 (tests/docs/demo/deploy readiness)

## First Phase to Start Immediately
Start **Phase 1** immediately: resolve password hashing compatibility, standardize environment configuration, and prove deterministic local startup with a short smoke test runbook.
