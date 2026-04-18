# Calisto AI Architecture (MVP Foundation)

## High-level design

Calisto AI is organized as a monorepo with a clear separation of concerns:

- `backend/`: FastAPI API and domain logic
- `frontend/`: React SPA
- `docs/`: architecture and standards documentation

## Backend layers

- **Routers**: HTTP boundary and request/response wiring.
- **Schemas**: Pydantic contracts for API validation and serialization.
- **Services**: Business logic (auth, document ingestion orchestration, chat answer synthesis).
- **Models**: SQLAlchemy entities for persistence.
- **DB**: SQLAlchemy session setup and dependency injection.

## Frontend layers

- **Layout shell**: persistent sidebar + main content area.
- **Route pages**: dashboard, documents, chat, and login.
- **Styling**: Tailwind utility classes with centralized style entrypoint.

## Data flow (future state)

1. User authenticates via JWT.
2. Tenant-scoped documents are uploaded and processed.
3. Document chunks are embedded and indexed in FAISS.
4. Chat requests trigger retrieval + LLM generation.
5. Answers return with source citations for grounding.

## Multi-tenant strategy (planned)

- Tenant ID propagated across auth, persistence, indexing, and querying.
- Tenant isolation enforced at query layer and service layer.
- Role-based controls define access to ingestion, admin config, and chat.
