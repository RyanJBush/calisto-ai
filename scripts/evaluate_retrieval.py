"""Retrieval-quality evaluation for Callisto.

Usage:
    # Start the API first (defaults to http://localhost:8000)
    make run-backend &
    python scripts/evaluate_retrieval.py

The script logs in as the seeded demo admin, uploads the sample documents
under ``data/samples/`` if they are not already present, then runs each
query from ``data/samples/eval_set.json`` against ``POST /api/chat/query``
and reports source-hit-rate, keyword-coverage, and mean latency.

This is intentionally a thin, dependency-light script (stdlib + requests)
so it can be wired into CI later without dragging in a notebook stack.
"""
from __future__ import annotations

import json
import os
import statistics
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:  # pragma: no cover
    print("This script requires the 'requests' package. Install with: pip install requests")
    sys.exit(2)


REPO_ROOT = Path(__file__).resolve().parents[1]
SAMPLES_DIR = REPO_ROOT / "data" / "samples"
EVAL_SET_PATH = SAMPLES_DIR / "eval_set.json"

API_BASE_URL = os.environ.get("CALISTO_API_BASE_URL", "http://localhost:8000")
DEMO_EMAIL = os.environ.get("CALISTO_DEMO_EMAIL", "admin@calisto.ai")
DEMO_PASSWORD = os.environ.get("CALISTO_DEMO_PASSWORD", "password123")
TOP_K = int(os.environ.get("CALISTO_EVAL_TOP_K", "3"))
SOURCE_HIT_RATE_THRESHOLD = float(os.environ.get("CALISTO_EVAL_THRESHOLD", "0.5"))


def login() -> str:
    resp = requests.post(
        f"{API_BASE_URL}/api/auth/login",
        json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def upload_samples(token: str) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    existing = requests.get(
        f"{API_BASE_URL}/api/documents", headers=headers, timeout=10
    ).json()
    existing_sources = {doc.get("source_name") for doc in existing}
    for path in sorted(SAMPLES_DIR.glob("*.txt")):
        if path.name in existing_sources:
            continue
        payload = {
            "title": path.stem.replace("_", " ").title(),
            "source_name": path.name,
            "content": path.read_text(encoding="utf-8"),
        }
        resp = requests.post(
            f"{API_BASE_URL}/api/documents/upload",
            json=payload,
            headers=headers,
            timeout=30,
        )
        if resp.status_code >= 400:
            print(f"  ! Failed to upload {path.name}: {resp.status_code} {resp.text}")
        else:
            print(f"  + Uploaded {path.name}")


def evaluate(token: str) -> int:
    eval_set = json.loads(EVAL_SET_PATH.read_text(encoding="utf-8"))
    headers = {"Authorization": f"Bearer {token}"}

    hits = 0
    keyword_scores: list[float] = []
    latencies_ms: list[float] = []

    print(f"\nEvaluating {len(eval_set['items'])} queries (top_k={TOP_K}) ...\n")
    print(f"{'Query':<55} {'src_hit':<8} {'kw_cov':<7} {'ms':<6}")
    print("-" * 80)

    for item in eval_set["items"]:
        query = item["query"]
        expected_sources = set(item.get("expected_sources", []))
        expected_keywords = [kw.lower() for kw in item.get("expected_keywords", [])]

        started = time.perf_counter()
        resp = requests.post(
            f"{API_BASE_URL}/api/chat/query",
            json={"query": query, "top_k": TOP_K, "grounded_mode": True},
            headers=headers,
            timeout=30,
        )
        elapsed_ms = (time.perf_counter() - started) * 1000
        latencies_ms.append(elapsed_ms)

        if resp.status_code >= 400:
            print(f"{query[:54]:<55} ERROR {resp.status_code}")
            continue

        body = resp.json()
        citations = body.get("citations", [])
        retrieved_sources = {c.get("document_title", "") for c in citations}
        retrieved_text = " ".join(c.get("snippet", "") for c in citations).lower()

        # Source hit if any expected source name appears in any retrieved title
        # (we lower-case + substring-match so "employee_handbook.txt" matches
        # the seeded "Employee Handbook" title).
        def matches(expected: str) -> bool:
            stem = expected.rsplit(".", 1)[0].replace("_", " ").lower()
            return any(stem in title.lower() for title in retrieved_sources)

        src_hit = any(matches(s) for s in expected_sources)
        if src_hit:
            hits += 1

        if expected_keywords:
            covered = sum(1 for kw in expected_keywords if kw in retrieved_text)
            kw_cov = covered / len(expected_keywords)
        else:
            kw_cov = 1.0
        keyword_scores.append(kw_cov)

        print(f"{query[:54]:<55} {'YES' if src_hit else 'no':<8} {kw_cov:<7.2f} {elapsed_ms:<6.0f}")

    n = len(eval_set["items"])
    hit_rate = hits / n if n else 0.0
    mean_kw = statistics.mean(keyword_scores) if keyword_scores else 0.0
    mean_lat = statistics.mean(latencies_ms) if latencies_ms else 0.0
    p95_lat = (
        statistics.quantiles(latencies_ms, n=20)[-1] if len(latencies_ms) >= 20 else max(latencies_ms or [0.0])
    )

    print("-" * 80)
    print(f"Source hit rate:     {hit_rate:.2%}   ({hits}/{n})")
    print(f"Keyword coverage:    {mean_kw:.2%}")
    print(f"Mean latency:        {mean_lat:.0f} ms")
    print(f"Max / ~p95 latency:  {p95_lat:.0f} ms")
    print(f"Threshold:           {SOURCE_HIT_RATE_THRESHOLD:.0%} source hit rate\n")

    return 0 if hit_rate >= SOURCE_HIT_RATE_THRESHOLD else 1


def main() -> int:
    if not EVAL_SET_PATH.exists():
        print(f"Eval set not found at {EVAL_SET_PATH}", file=sys.stderr)
        return 2
    try:
        token = login()
    except requests.RequestException as exc:
        print(f"Could not reach the API at {API_BASE_URL}: {exc}", file=sys.stderr)
        print("Start the backend first (e.g. `make run-backend`).", file=sys.stderr)
        return 2
    upload_samples(token)
    return evaluate(token)


if __name__ == "__main__":
    sys.exit(main())
