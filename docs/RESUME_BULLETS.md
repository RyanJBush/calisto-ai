# Resume Bullets — Callisto

These bullets are written to stay technically honest.

## Safe headline bullet

- Built **Callisto**, a local portfolio demo of an enterprise-style RAG knowledge platform using FastAPI, React, SQLAlchemy, and Docker, with document ingestion, hybrid retrieval, weighted reranking, grounded citation output, JWT auth, and org-scoped RBAC.

## Additional bullets

- Implemented a full retrieval pipeline (chunking, embedding, indexing, retrieval, reranking, citation assembly) with clear service boundaries for swapping model providers.
- Designed deterministic hash-embedding and heuristic answer defaults so the system runs fully offline, reproducibly, and without API keys.
- Added organization-scoped filtering and role checks to demonstrate multi-tenant and RBAC patterns in a RAG application.
- Built and documented API endpoints for auth, document management, chat/query workflows, and admin metrics.
- Structured backend logic in layered modules (routers/services/models/schemas) for readability and maintainability.

## Wording to avoid unless upgraded

Do **not** claim these unless you actually implement them:
- “LLM-generated answers”
- “Cross-encoder reranking”
- “Semantic embeddings from transformer models”
- “Production enterprise deployment”

Use this phrasing instead:
- “Heuristic grounded answer composition”
- “Weighted reranking”
- “Deterministic hash embeddings”
- “Local portfolio demo / enterprise-style architecture”

