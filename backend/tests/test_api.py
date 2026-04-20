from fastapi.testclient import TestClient
import time

from app.main import app


def auth_header(email: str, password: str = "password123") -> dict[str, str]:
    with TestClient(app) as client:
        response = client.post("/api/auth/login", json={"email": email, "password": password})
        token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health_endpoint() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "ok"


def test_auth_login_and_me() -> None:
    with TestClient(app) as client:
        login = client.post(
            "/api/auth/login",
            json={"email": "admin@calisto.ai", "password": "password123"},
        )
        assert login.status_code == 200
        token = login.json()["access_token"]

        me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me.status_code == 200
        assert me.json()["role"] == "admin"


def test_document_chat_flow_with_citations() -> None:
    headers = auth_header("member@calisto.ai")

    with TestClient(app) as client:
        upload = client.post(
            "/api/documents/upload",
            headers=headers,
            json={
                "title": "Employee Handbook",
                "content": "Calisto AI supports citation-based answers and enterprise RBAC policies.",
                "source_name": "handbook.txt",
            },
        )
        assert upload.status_code == 200
        doc_id = upload.json()["id"]
        assert upload.json()["ingestion_status"] in {"queued", "processing", "completed"}
        assert upload.json()["version"] >= 1

        for _ in range(20):
            detail = client.get(f"/api/documents/{doc_id}", headers=headers)
            assert detail.status_code == 200
            if detail.json()["ingestion_status"] == "completed":
                break
            time.sleep(0.1)
        assert detail.json()["ingestion_status"] == "completed"
        assert detail.json()["ingestion_attempts"] >= 1

        listed = client.get("/api/documents", headers=headers)
        assert listed.status_code == 200
        assert any(doc["id"] == doc_id for doc in listed.json())

        assert len(detail.json()["chunks"]) > 0

        query = client.post(
            "/api/chat/query",
            headers=headers,
            json={
                "query": "How does Calisto answer questions in handbook?",
                "filters": {"source_name": "handbook"},
            },
        )
        assert query.status_code == 200
        payload = query.json()
        assert payload["session_id"] > 0
        assert len(payload["citations"]) >= 1
        assert payload["confidence_score"] >= 0
        assert payload["citation_coverage"] >= 0
        assert payload["rewritten_query"]
        assert "source_preview" in payload["citations"][0]
        assert payload["citations"][0]["highlight_end"] > payload["citations"][0]["highlight_start"]
        assert len(payload["citations"][0]["highlight_ranges"]) >= 1
        assert "retrieval_score" in payload["citations"][0]

        ingestion_runs = client.get(f"/api/documents/{doc_id}/ingestion-runs", headers=headers)
        assert ingestion_runs.status_code == 200
        assert len(ingestion_runs.json()) >= 1
        assert ingestion_runs.json()[0]["status"] in {"processing", "completed", "failed"}

        history = client.get("/api/chat/history", headers=headers)
        assert history.status_code == 200
        assert len(history.json()) >= 2


def test_duplicate_document_detection_and_versioning() -> None:
    headers = auth_header("member@calisto.ai")

    with TestClient(app) as client:
        first = client.post(
            "/api/documents/upload",
            headers=headers,
            json={"title": "Roadmap", "content": "Q3 milestones for Calisto", "source_name": "roadmap.md"},
        )
        assert first.status_code == 200
        assert first.json()["version"] >= 1

        duplicate = client.post(
            "/api/documents/upload",
            headers=headers,
            json={"title": "Roadmap", "content": "Q3 milestones for Calisto", "source_name": "roadmap.md"},
        )
        assert duplicate.status_code == 409

        second_version = client.post(
            "/api/documents/upload",
            headers=headers,
            json={"title": "Roadmap", "content": "Q4 milestones for Calisto", "source_name": "roadmap.md"},
        )
        assert second_version.status_code == 200
        assert second_version.json()["version"] == first.json()["version"] + 1


def test_viewer_cannot_upload_documents() -> None:
    headers = auth_header("viewer@calisto.ai")

    with TestClient(app) as client:
        upload = client.post(
            "/api/documents/upload",
            headers=headers,
            json={"title": "Viewer Doc", "content": "should fail"},
        )
        assert upload.status_code == 403


def test_admin_analytics_summary_authorization() -> None:
    admin_headers = auth_header("admin@calisto.ai")
    member_headers = auth_header("member@calisto.ai")

    with TestClient(app) as client:
        member_response = client.get("/api/admin/analytics/summary", headers=member_headers)
        assert member_response.status_code == 403

        admin_response = client.get("/api/admin/analytics/summary", headers=admin_headers)
        assert admin_response.status_code == 200
        payload = admin_response.json()
        assert payload["documents_total"] >= 0
        assert payload["chunks_total"] >= 0
        assert payload["chat_sessions_total"] >= 0
        assert payload["queries_total"] >= 0
        assert payload["ingestions_queued"] >= 0

        top_documents = client.get("/api/admin/analytics/top-documents", headers=admin_headers)
        assert top_documents.status_code == 200
        assert isinstance(top_documents.json(), list)
        if top_documents.json():
            assert "indexed_chunks" in top_documents.json()[0]

        ingestion_breakdown = client.get("/api/admin/analytics/ingestion-breakdown", headers=admin_headers)
        assert ingestion_breakdown.status_code == 200
        assert isinstance(ingestion_breakdown.json(), list)
