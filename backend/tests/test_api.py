from fastapi.testclient import TestClient

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
        assert upload.json()["ingestion_status"] == "completed"

        listed = client.get("/api/documents", headers=headers)
        assert listed.status_code == 200
        assert any(doc["id"] == doc_id for doc in listed.json())

        detail = client.get(f"/api/documents/{doc_id}", headers=headers)
        assert detail.status_code == 200
        assert len(detail.json()["chunks"]) > 0

        query = client.post(
            "/api/chat/query",
            headers=headers,
            json={"query": "How does Calisto answer questions?"},
        )
        assert query.status_code == 200
        payload = query.json()
        assert payload["session_id"] > 0
        assert len(payload["citations"]) >= 1
        assert "source_preview" in payload["citations"][0]
        assert payload["citations"][0]["highlight_end"] > payload["citations"][0]["highlight_start"]
        assert "retrieval_score" in payload["citations"][0]

        history = client.get("/api/chat/history", headers=headers)
        assert history.status_code == 200
        assert len(history.json()) >= 2


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
