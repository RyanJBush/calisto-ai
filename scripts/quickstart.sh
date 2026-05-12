#!/usr/bin/env bash
# Quickstart for Callisto. Installs deps, runs migrations, starts the API and frontend.
#
# Usage: ./scripts/quickstart.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> Installing backend deps"
python -m pip install --upgrade pip
pip install -r backend/requirements.txt

echo "==> Initializing local SQLite database (idempotent)"
( cd backend && PYTHONPATH=. python scripts/init_db.py )

echo "==> Installing frontend deps"
( cd frontend && npm ci )

cat <<EOF

Setup complete. Open two terminals and run:

  1) make run-backend     # FastAPI on http://localhost:8000  (docs at /docs)
  2) make run-frontend    # Vite on    http://localhost:5173

Seeded demo credentials:
  admin@calisto.ai  /  password123
  member@calisto.ai /  password123

Then, optionally, run the retrieval-eval script:
  python scripts/evaluate_retrieval.py
EOF
