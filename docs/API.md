# API Reference

Base URL (local): `http://localhost:8000`

All endpoints under `/api/*` require a Bearer token from `/api/auth/login`.
Interactive OpenAPI docs are served at `http://localhost:8000/docs` when
the backend is running.

## Authentication

### `POST /api/auth/register`
Register a new user under an organization.

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "alice@acme.test",
    "password": "ChangeMe123!",
    "organization_name": "Acme Corp"
  }'
```

### `POST /api/auth/login`
Exchange credentials for a JWT.

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"alice@acme.test","password":"ChangeMe123!"}'
```

Response:
```json
{ "access_token": "eyJ...", "token_type": "bearer" }
```

Export it for later calls:
```bash
export TOKEN="eyJ..."
```

## Documents

### `POST /api/documents/upload`
Upload a text document. The ingestion pipeline chunks the content, embeds
each chunk, and indexes it against the requesting user's organization.

```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "Employee Handbook",
    "source_name": "employee_handbook.txt",
    "content": "Full-time employees are expected to work 40 hours per week..."
  }'
```

### `GET /api/documents`
List documents the current user can read.

### `GET /api/documents/{document_id}`
Get a document and its chunks.

### `POST /api/documents/collections`
Create a collection (a logical group of documents within an organization).

### `POST /api/documents/{document_id}/access` (admin only)
Grant another user access to a specific document.

## Chat / Retrieval

### `POST /api/chat/query`
Ask a question. The server retrieves the top chunks scoped to the user's
organization, optionally reranks them, and returns a grounded answer with
inline citations.

```bash
curl -X POST http://localhost:8000/api/chat/query \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "How many PTO days do new employees get?",
    "top_k": 3,
    "grounded_mode": true
  }'
```

Response (truncated):
```json
{
  "session_id": 1,
  "answer": "Based on the indexed knowledge base:\n\n[1] Employees accrue 15 days...",
  "answer_mode": "grounded_heuristic",
  "confidence_score": 0.72,
  "citation_coverage": 1.0,
  "insufficient_evidence": false,
  "citations": [
    {
      "document_title": "Employee Handbook",
      "chunk_id": 42,
      "retrieval_score": 0.81,
      "snippet": "Employees accrue 15 days of paid time off..."
    }
  ],
  "latency_breakdown_ms": { "retrieve": 12, "rerank": 3, "generate": 1 }
}
```

### `GET /api/chat/history`
Return the current user's chat messages.

### `POST /api/chat/feedback`
Submit a thumbs-up / thumbs-down rating on a previous assistant message.

## Admin

### `GET /api/admin/metrics`
Aggregate request count, average latency, and recent audit events. Admin role
required.

## Health

### `GET /health`
Liveness check. Returns `{"status": "ok"}`.
