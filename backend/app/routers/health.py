from fastapi import APIRouter

from app.core.metrics import metrics_store

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str | int]:
    return {"status": "ok", "requests_seen": metrics_store.request_count}


@router.get("/metrics")
def metrics() -> dict[str, int]:
    return {"requests_total": metrics_store.request_count}
