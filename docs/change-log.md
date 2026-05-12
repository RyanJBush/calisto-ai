# Callisto Change Log

## 2026-05-12

### README and documentation updates
- Rewrote `README.md` with a recruiter-focused structure, grounded feature descriptions, and explicit implementation honesty notes.
- Updated `docs/resume-bullets.md` to concise action-verb bullets focused on retrieval and indexing design.
- Updated `docs/screenshots/README.md` to reflect actual screenshot files and added a TODO checklist for missing capture types.

### Dev experience updates
- Clarified one-command setup/run flow in README using `make bootstrap` and `make dev`.
- Added a lightweight smoke test script (`scripts/smoke_test.py`) for import and sample-data sanity checks.

### Portfolio preview updates
- Refined `docs/preview/index.html` into a mobile-friendly, self-contained design preview with:
  - dark teal/slate visual style,
  - clear feature cards,
  - tech badges,
  - inline SVG architecture diagram,
  - 30-second “How it works” section.

### Corrected/softened claims
- Replaced inflated language with demo-scale wording.
- Clarified that default behavior uses deterministic hash-based embeddings, weighted reranking, and heuristic/template-based answer synthesis.
