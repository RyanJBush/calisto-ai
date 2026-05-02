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


def test_auth_login_rejects_invalid_credentials() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/auth/login",
            json={"email": "admin@calisto.ai", "password": "wrong-password"},
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"


def test_document_chat_flow_with_citations() -> None:
    headers = auth_header("member@calisto.ai")

    with TestClient(app) as client:
        source_name = f"handbook-{int(time.time() * 1000)}.txt"
        collection = client.post(
            "/api/documents/collections",
            headers=headers,
            json={"name": f"Employee Docs {int(time.time() * 1000)}"},
        )
        assert collection.status_code == 200

        upload = client.post(
            "/api/documents/upload",
            headers=headers,
            json={
                "title": "Employee Handbook",
                "content": "Calisto AI supports citation-based answers and enterprise RBAC policies.",
                "source_name": source_name,
                "collection_id": collection.json()["id"],
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
                "filters": {"source_name": source_name, "collection_id": collection.json()["id"]},
            },
        )
        assert query.status_code == 200
        payload = query.json()
        assert payload["session_id"] > 0
        assert payload["assistant_message_id"] > 0
        assert len(payload["citations"]) >= 1
        assert payload["confidence_score"] >= 0
        assert payload["citation_coverage"] >= 0
        assert payload["rewritten_query"]
        assert payload["answer_mode"]
        assert isinstance(payload["evidence_summary"], list)
        assert payload["latency_breakdown_ms"]["total"] >= 0
        assert "source_preview" in payload["citations"][0]
        assert payload["citations"][0]["highlight_end"] > payload["citations"][0]["highlight_start"]
        assert len(payload["citations"][0]["highlight_ranges"]) >= 1
        assert "retrieval_score" in payload["citations"][0]

        feedback = client.post(
            "/api/chat/feedback",
            headers=headers,
            json={"message_id": payload["assistant_message_id"], "rating": 1, "comment": "Good answer"},
        )
        assert feedback.status_code == 200
        assert feedback.json()["rating"] == 1

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
        source_name = f"roadmap-{int(time.time() * 1000)}.md"

        first = client.post(
            "/api/documents/upload",
            headers=headers,
            json={"title": "Roadmap", "content": "Q3 milestones for Calisto", "source_name": source_name},
        )
        assert first.status_code == 200
        assert first.json()["version"] >= 1

        duplicate = client.post(
            "/api/documents/upload",
            headers=headers,
            json={"title": "Roadmap", "content": "Q3 milestones for Calisto", "source_name": source_name},
        )
        assert duplicate.status_code == 409

        second_version = client.post(
            "/api/documents/upload",
            headers=headers,
            json={"title": "Roadmap", "content": "Q4 milestones for Calisto", "source_name": source_name},
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


def test_document_access_grants_for_viewer() -> None:
    admin_headers = auth_header("admin@calisto.ai")
    member_headers = auth_header("member@calisto.ai")
    viewer_headers = auth_header("viewer@calisto.ai")

    with TestClient(app) as client:
        upload = client.post(
            "/api/documents/upload",
            headers=member_headers,
            json={"title": "Restricted Doc", "content": "viewer should access after grant", "source_name": f"restricted-{int(time.time() * 1000)}.txt"},
        )
        assert upload.status_code == 200
        doc_id = upload.json()["id"]

        viewer_list_before = client.get("/api/documents", headers=viewer_headers)
        assert viewer_list_before.status_code == 200
        assert all(doc["id"] != doc_id for doc in viewer_list_before.json())

        grant = client.post(
            f"/api/documents/{doc_id}/access",
            headers=admin_headers,
            json={"user_id": 3, "permission": "read"},
        )
        assert grant.status_code == 200

        viewer_list_after = client.get("/api/documents", headers=viewer_headers)
        assert viewer_list_after.status_code == 200
        assert any(doc["id"] == doc_id for doc in viewer_list_after.json())


def test_admin_can_revoke_document_access_for_viewer() -> None:
    admin_headers = auth_header("admin@calisto.ai")
    member_headers = auth_header("member@calisto.ai")
    viewer_headers = auth_header("viewer@calisto.ai")

    with TestClient(app) as client:
        upload = client.post(
            "/api/documents/upload",
            headers=member_headers,
            json={
                "title": "Private Doc",
                "content": "viewer access should be revoked",
                "source_name": f"private-{int(time.time() * 1000)}.txt",
            },
        )
        assert upload.status_code == 200
        doc_id = upload.json()["id"]

        grant = client.post(
            f"/api/documents/{doc_id}/access",
            headers=admin_headers,
            json={"user_id": 3, "permission": "read"},
        )
        assert grant.status_code == 200

        visible_before = client.get("/api/documents", headers=viewer_headers)
        assert any(doc["id"] == doc_id for doc in visible_before.json())

        revoke = client.delete(f"/api/documents/{doc_id}/access/3", headers=admin_headers)
        assert revoke.status_code == 204

        visible_after = client.get("/api/documents", headers=viewer_headers)
        assert all(doc["id"] != doc_id for doc in visible_after.json())


def test_revoke_document_access_returns_404_when_grant_missing() -> None:
    admin_headers = auth_header("admin@calisto.ai")

    with TestClient(app) as client:
        response = client.delete("/api/documents/999999/access/3", headers=admin_headers)
        assert response.status_code == 404
        assert response.json()["detail"] == "Document access grant not found."


def test_feedback_requires_existing_assistant_message_for_current_user() -> None:
    member_headers = auth_header("member@calisto.ai")

    with TestClient(app) as client:
        response = client.post(
            "/api/chat/feedback",
            headers=member_headers,
            json={"message_id": 999999, "rating": -1, "comment": "not found"},
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Assistant message not found for this user."


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

        audit_logs = client.get("/api/admin/audit-logs", headers=admin_headers)
        assert audit_logs.status_code == 200
        assert isinstance(audit_logs.json(), list)

        feedback_summary = client.get("/api/admin/analytics/feedback-summary", headers=admin_headers)
        assert feedback_summary.status_code == 200
        assert "total_feedback" in feedback_summary.json()

        benchmark = client.get("/api/admin/analytics/benchmark", headers=admin_headers)
        assert benchmark.status_code == 200
        assert "pass_rate" in benchmark.json()

        collections = client.get("/api/admin/analytics/collections", headers=admin_headers)
        assert collections.status_code == 200
        assert isinstance(collections.json(), list)
