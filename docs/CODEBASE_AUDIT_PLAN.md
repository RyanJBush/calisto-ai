# Calisto AI — Audit, Prioritized Improvements, and Implementation Plan

## 1) Codebase Audit (Current State)

### Repository and runtime setup
- Monorepo layout is clear and production-leaning: `backend` (FastAPI), `frontend` (React/Vite), `docs`, Docker and Make targets at root.  
- `README.md` setup instructions are generally coherent and reflect primary flows (bootstrap, migrate, run API/UI).  
- Docker and local tooling exist, enabling a runnable local environment.

### Backend (FastAPI)
- Routers are split by domain (`auth`, `documents`, `chat`, `admin`, `health`) with corresponding schemas and service layers.  
- Models cover key enterprise entities: organizations, users/roles, documents/chunks, ingestion runs, chats/messages, feedback, and audit logs.  
- Core controls are present (JWT auth, dependencies, rate limiting module, metrics/logging modules).

### Database and schema management
- SQLAlchemy models are reasonably complete.  
- Alembic is present with initial migration scaffolding, but migration discipline and coverage still need hardening for future schema evolution.

### Ingestion, embeddings, retrieval, and answer pipeline
- Ingestion service path exists and supports chunking + embedding/indexing lifecycle.  
- Retrieval stack includes vector retrieval components and additional services such as rerank/query rewrite abstractions.  
- Citation-bearing chat responses are implemented through chat/answer services and schemas.

### Frontend (React)
- Core pages exist: Login, Dashboard, Documents, Chat, Settings with app shell components.  
- API service layer exists and maps major user flows.  
- UX is functional but not yet “enterprise polished” in status visibility, source exploration, and workflow depth.

### Tests and quality gates
- Backend tests are substantial and currently pass in this environment.  
- Frontend production build succeeds.  
- Gaps: frontend unit/integration tests and full e2e scenarios are not yet comprehensive.

### Verification checks run
- Backend tests: pass (`pytest tests -q`).
- Frontend build: pass (`npm run build`).

---

## 2) Prioritized Improvements (High Impact)

## P0 — Critical for “polished runnable platform”
1. **Reliability hardening of end-to-end ingestion->retrieval->chat**
   - Add stronger ingestion job durability semantics (resume/retry/error classification).
   - Ensure index consistency and startup rebuild/reconciliation path.
2. **Security and correctness hardening**
   - Validate all high-risk inputs (upload metadata, filters, sort fields, pagination, prompt/query fields).
   - Tighten auth/session lifecycle (token TTL strategy, rotation/revocation approach, audit trail completeness).
3. **Migration and environment hygiene**
   - Enforce strict migration workflow and environment contract (`.env.example`, startup validation).

## P1 — Product-defining RAG enhancements
1. **Hybrid retrieval (keyword + vector) with tunable weighting**.
2. **Reranking improvements** (configurable provider/pipeline, fallback behavior, score attribution).
3. **Document-level permissions enforcement** (backend complete + UI admin controls).
4. **Background ingestion jobs with user-visible progress states**.

## P2 — Enterprise UX and governance value
1. **User feedback loop** on answers (thumbs + reason taxonomy + optional freeform notes).
2. **Admin analytics** (ingestion throughput, retrieval hit quality, citation coverage, usage by org/user).
3. **Saved chats / conversation management**.
4. **Source preview UX** (chunk highlight, jump-to-source, relevance explanation badges).

## P3 — Quality, maintainability, and demo readiness
1. **Evaluation metrics suite** (retrieval precision@k proxy, citation precision, groundedness heuristics).
2. **Automated test expansion** (frontend unit tests + backend integration + e2e happy paths).
3. **Documentation/runbooks** (ops troubleshooting, security posture, data lifecycle).

---

## 3) Security/Code-Quality/UX Findings to Address

### Security & robustness
- Some endpoints/services need stricter input contracts and consistent error code mapping.
- Rate limiting and abuse controls should be made policy-driven (per-role/per-route/per-org).
- Secrets/config handling should include startup-time required variable checks and non-dev safe defaults.

### Code quality
- Pydantic v2 deprecation warnings are present for class-based `Config`; migrate to `ConfigDict` to avoid future breakage.
- Service boundaries are good, but background workers and retrieval orchestration will benefit from clearer interface contracts and typed exceptions.

### UI/UX
- Add richer loading/empty/error states across Documents and Chat.
- Improve citation visual hierarchy and source readability.
- Add operational cards on Dashboard (ingestion queue, failure rate, feedback trends).

---

## 4) Phased Implementation Plan (Do not code yet)

## Phase 1 — Make app reliably runnable and fix critical issues
**Goal:** deterministic local startup and stable core flows.

**Modules/files to prioritize**
- Backend config/startup/auth/dependencies: `backend/app/config.py`, `backend/app/main.py`, `backend/app/core/*`
- DB bootstrap/migrations: `backend/alembic/*`, `backend/app/db/*`
- Dev setup docs/scripts: `README.md`, `Makefile`, `docker-compose.yml`

**Tasks**
- Add strict env validation and defaults for local/dev.
- Confirm migration-first boot path and remove schema drift risks.
- Standardize startup checks (DB connectivity, required tables/indexes, optional index warmup).
- Resolve deprecation warnings that risk near-term breakage (Pydantic Config migration).

**Dependencies**
- Python package/version alignment; database extension availability where required.

**Success criteria**
- Fresh clone + documented commands produce running backend/frontend.
- Auth login, document upload initiation, and chat query endpoints respond successfully.

## Phase 2 — Complete core ingestion and retrieval end-to-end
**Goal:** robust upload -> embedding -> retrieval -> chat with citations.

**Modules/files to prioritize**
- Ingestion and jobs: `backend/app/services/ingestion_service.py`, `ingestion_job_service.py`, `backend/app/routers/documents.py`
- Embeddings/vector/retrieval: `backend/app/services/embedding_service.py`, `vector_store.py`, `retrieval_service.py`, `embedding_index_service.py`
- Chat/answer path: `backend/app/services/chat_service.py`, `answer_service.py`, `backend/app/routers/chat.py`
- UI flow: `frontend/src/pages/DocumentsPage.jsx`, `frontend/src/pages/ChatPage.jsx`, `frontend/src/services/api.js`

**Tasks**
- Harden async ingestion lifecycle/state transitions and failure recovery.
- Guarantee index/document consistency and deterministic citation payload structure.
- Improve retrieval relevance defaults and traceability (scores/components).
- Ensure citations map clearly to document/chunk metadata consumed by UI.

**Dependencies**
- Storage/index backend strategy and job execution model decisions.

**Success criteria**
- User can upload document(s), observe status completion, ask questions, and receive grounded answers with usable citations.

## Phase 3 — Implement key enhancements
**Goal:** deliver high-impact enterprise RAG features.

**Modules/files to prioritize**
- Retrieval/rerank/query rewrite: `backend/app/services/retrieval_service.py`, `rerank_service.py`, `query_rewrite_service.py`
- Admin analytics + feedback: `backend/app/routers/admin.py`, `backend/app/services/admin_service.py`, `backend/app/models/chat_feedback.py`, `backend/app/routers/chat.py`
- Permissions: `backend/app/models/document_access.py`, `backend/app/services/document_service.py`, related documents router/UI

**Tasks**
- Implement/tune hybrid retrieval with weighted blending.
- Integrate reranking pipeline with clear fallback and telemetry.
- Capture answer feedback and expose admin analytics endpoints/cards.
- Add complete document-level ACL management (grant/revoke/list) in API + UI.

**Dependencies**
- Metric definitions for analytics and storage strategy for feedback telemetry.

**Success criteria**
- Measurable retrieval quality lift, visible analytics, and enforceable per-document access controls.

## Phase 4 — Polish UX, security, tests, docs
**Goal:** ship a polished internal knowledge platform.

**Modules/files to prioritize**
- UX/UI: `frontend/src/pages/*`, `frontend/src/components/*`, `frontend/src/layouts/*`
- Security/core: `backend/app/core/security.py`, `backend/app/core/dependencies.py`, auth services/routers
- Test suites: `backend/tests/*`, add frontend test harness and e2e
- Documentation: `README.md`, `docs/ARCHITECTURE.md`, operational runbooks

**Tasks**
- Add source preview interactions, ingestion status surfaces, saved chats, optional dark mode.
- Tighten auth/session and input-validation security posture.
- Add frontend tests + cross-layer integration/e2e checks.
- Update docs for operators/developers with troubleshooting and performance guidance.

**Dependencies**
- Final UX design decisions and test environment fixtures.

**Success criteria**
- Platform is demonstrably stable, secure-by-default, test-covered, and polished for internal enterprise usage.

---

## 5) Immediate Next Execution Order (after approval)
1. Phase 1 hardening PR (runnability + deprecations + env/migration checks).
2. Phase 2 ingestion/retrieval reliability PR.
3. Phase 3 feature PR (hybrid/rerank/analytics/feedback/ACL).
4. Phase 4 UX/security/testing/docs PR.
