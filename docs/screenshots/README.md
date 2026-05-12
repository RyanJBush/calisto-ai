# Screenshots

This directory holds UI screenshots that are referenced from the top-level
`README.md`. Captures were taken at 1440×900 against a locally-running
backend (`uvicorn app.main:app`) and frontend (`vite dev`) with the seeded
demo data from `backend/scripts/init_db.py`.

All target routes already exist in `frontend/src/pages/`.

## Required captures

| File | Capture | Source page / route |
|---|---|---|
| `documents.png` | Document upload — upload form, file list, chunk preview after ingestion | `DocumentsPage` |
| `chat.png` | Chat with inline citations — query box, grounded answer, citation list with chunk IDs and snippets | `ChatPage` |
| `admin.png` | Admin / RBAC page — user list, role assignment, admin-only tools | `SettingsPage` (admin view) |
| `api-docs.png` | API docs — FastAPI Swagger UI at `http://localhost:8000/docs` showing the 15 endpoints grouped by router | `/docs` on the backend |

## Optional / nice-to-have captures

| File | Capture | Source page / route |
|---|---|---|
| `dashboard.png` | Dashboard overview — stats + recent activity | `DashboardPage` |
| `audit.png` | Audit log view — ingestion / retrieval / admin events | admin section of `SettingsPage` or `/api/admin/metrics` JSON |
| `metrics.png` | Metrics — request count, average latency, recent events | admin section of `SettingsPage` |
| `document-detail.png` | Document detail — chunks list with embeddings metadata | `DocumentsPage` detail view |

## How to reference them from the README

Once a file is added here, link it from the top-level `README.md` like:

```markdown
![Chat with citations](docs/screenshots/chat.png)
```

Or as a small responsive thumbnail:

```markdown
<img src="docs/screenshots/chat.png" alt="Chat with citations" width="720">
```

## Capture tips

- Use a 1440×900 viewport for consistency across captures.
- Crop to the meaningful UI region; avoid OS chrome and browser toolbars.
- Prefer PNG over JPEG so text stays crisp.
- For the API docs capture, expand a couple of representative endpoints
  (e.g. `POST /api/chat/query`) so the request/response schema is visible.
- For the chat capture, ask one of the seeded eval questions
  (*"How many PTO days do employees get?"*) so the citation list is non-empty.
- Do not include the actual JWT or any secrets in the screenshot.

## Status

- [x] `documents.png` — Documents page (upload form, library, ingestion status)
- [x] `chat.png` — Chat with the seeded PTO question, grounded answer, 3
      citations with chunk IDs, source preview, latency mode
- [x] `admin.png` — Settings page (see note below)
- [x] `api-docs.png` — full Swagger UI showing all 15 endpoints grouped under
      `health`, `auth`, `documents`, `chat`, `admin`, with `POST /api/chat/query`
      expanded
- [x] `dashboard.png` — Dashboard with documents/queries/latency counters and
      top-indexed documents
- [x] `audit.png` — pretty-printed `GET /api/admin/audit-logs` JSON response
- [x] `metrics.png` — pretty-printed `GET /api/admin/analytics/summary` JSON
      response
- [ ] `document-detail.png` (optional) — not captured; the current
      `DocumentsPage` renders all documents on the same page rather than a
      separate detail route, so a dedicated detail view is not reachable from
      the UI yet

### Known gap — `admin.png`

The current `frontend/src/pages/SettingsPage.jsx` is a placeholder card with the
text *"Configure organization defaults, model providers, and retrieval
policies in future iterations."* — it does **not** yet render a user list,
role assignment, or admin-only tools. The screenshot reflects that.

The underlying RBAC and admin endpoints (`/api/admin/...`) are real and
working; their JSON responses are captured in `metrics.png` and `audit.png`
as a stand-in. Building out the Settings UI to surface those endpoints is
follow-up work.
