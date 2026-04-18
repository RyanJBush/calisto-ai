def test_upload_text_document(client, auth_token: str) -> None:
    response = client.post(
        "/api/v1/documents/upload",
        data={"title": "MVP Notes", "text_input": "Calisto supports citation-based answers."},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["document_id"] > 0
    assert payload["chunk_count"] >= 1
    assert len(payload["chunks"]) == payload["chunk_count"]


def test_upload_requires_auth(client) -> None:
    response = client.post(
        "/api/v1/documents/upload",
        data={"title": "No Auth", "text_input": "should fail"},
    )
    assert response.status_code == 401
