# Resume Bullets — Callisto

- Built a full-stack RAG portfolio demo that ingests documents, chunks content, and returns citation-grounded answers.
- Implemented hybrid retrieval that blends lexical BM25-style scoring with vector similarity for document search.
- Designed weighted reranking logic to reorder candidate chunks using transparent, configurable feature weights.
- Created deterministic hash-based embedding defaults so the system runs locally without external model API keys.
- Structured FastAPI services for ingestion, retrieval, synthesis, and auth to keep components testable and replaceable.
- Added role-based access controls and organization-scoped filtering to demonstrate multi-tenant access patterns.
