"""Small smoke test for local Callisto development.

Checks:
1) Backend app imports cleanly.
2) Sample data files required for demo/eval are present.

Usage:
    python scripts/smoke_test.py
"""
from __future__ import annotations

from pathlib import Path
import sys


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    backend_dir = repo_root / "backend"
    if not backend_dir.exists():
        print("[FAIL] backend/ directory not found")
        return 2

    sys.path.insert(0, str(backend_dir))

    try:
        from app.main import app  # noqa: F401
    except Exception as exc:  # pragma: no cover - explicit smoke failure path
        print(f"[FAIL] Could not import backend app.main: {exc}")
        return 1

    required = [
        repo_root / "data" / "samples" / "employee_handbook.txt",
        repo_root / "data" / "samples" / "security_policy.txt",
        repo_root / "data" / "samples" / "eval_set.json",
    ]
    missing = [str(path.relative_to(repo_root)) for path in required if not path.exists()]
    if missing:
        print("[FAIL] Missing required sample files:")
        for item in missing:
            print(f"  - {item}")
        return 2

    print("[PASS] Smoke test succeeded: backend import + sample dataset checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
