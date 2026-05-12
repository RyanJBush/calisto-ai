# Screenshots

This directory holds UI screenshots that are referenced from the top-level
`README.md`. **No screenshots have been captured yet for the published repo.**
The list below is the target set — drop the files in here using the suggested
names and they will line up with the README references.

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

- [ ] `documents.png`
- [ ] `chat.png`
- [ ] `admin.png`
- [ ] `api-docs.png`
- [ ] `dashboard.png` (optional)
- [ ] `audit.png` (optional)
- [ ] `metrics.png` (optional)
- [ ] `document-detail.png` (optional)

Until these are captured, the README links here rather than embedding broken
images, and the *Screenshots / Demo* section in the top-level README is
explicit that captures are pending.
