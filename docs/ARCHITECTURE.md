# Architecture

Calisto AI is organized as a monorepo with explicit separation between backend API services and frontend application delivery.

## High-Level Components

- **Frontend (`/frontend`)**: React + Vite SPA for user workflows (auth, dashboard, documents, chat, settings)
- **Backend (`/backend`)**: FastAPI application with modular clean architecture
- **Database (PostgreSQL)**: Core relational data for users, orgs, docs, chunks, chat sessions/messages
- **Vector Retrieval Layer**: `VectorStore` interface with FAISS-style MVP implementation and provider-swappable design

## Backend Layering

- `routers/` HTTP route handlers
- `schemas/` request/response contracts
- `services/` domain workflows (ingestion, embedding, retrieval, answering)
- `models/` SQLAlchemy ORM entities
- `db/` engine/session/bootstrap and seed data
- `core/` auth, logging, metrics, shared dependencies

## RAG Flow (MVP)

1. User uploads text document
2. Ingestion service chunks the text
3. Embedding service generates deterministic placeholder vectors
4. Vector store indexes chunk vectors for retrieval
5. Chat query embeds user question and retrieves top chunks
6. Answer service returns synthesized answer + citations
