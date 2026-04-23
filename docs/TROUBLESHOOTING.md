# Troubleshooting

## Backend fails to start with JWT secret error
- Cause: production environment with default JWT secret.
- Fix: set `JWT_SECRET` in `backend/.env` to a strong random value.

## Tests fail with stale state
- Use `make test` (already isolates to `test.db`).
- If needed manually remove `backend/test.db`.

## PDF upload fails
- Ensure `pypdf` is installed from backend requirements.
- Verify uploaded PDFs contain extractable text (not image-only scans).

## No documents returned in chat
- Ensure ingestion is completed for uploaded docs.
- Retry ingestion from Documents page or `/api/documents/{id}/retry-ingestion`.

## 401 loops in frontend
- Token is automatically cleared on 401 and user is redirected to login.
- Re-authenticate and retry.
