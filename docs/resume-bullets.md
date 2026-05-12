# Resume Bullets — Callisto

- Built a demo-scale RAG knowledge platform using FastAPI, React, SQLAlchemy, PostgreSQL, and Docker with document ingestion, retrieval, and citation-backed response assembly.
- Implemented a retrieval pipeline that combines lexical and vector signals with weighted reranking to improve result ordering for document-grounded queries.
- Designed deterministic hash-based embeddings and heuristic answer synthesis defaults so the project runs locally without external model API keys.
- Structured backend modules across routers, services, models, and schemas to keep interfaces explicit and provider swaps straightforward.
- Added JWT authentication, role-based access controls, and organization-scoped filtering to demonstrate multi-tenant access patterns.
- Documented architecture and demo workflows in `docs/ARCHITECTURE.md` and `docs/DEMO_RUNBOOK.md` to support recruiter and interviewer walkthroughs.
