def test_query_returns_citations_and_chunks(client, auth_token: str) -> None:
    ingest = client.post(
        "/api/v1/documents/upload",
        data={
            "title": "SOC2 Policy",
            "text_input": "The SOC2 policy requires quarterly access review and annual penetration tests.",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert ingest.status_code == 200

    response = client.post(
        "/api/v1/chat/query",
        json={"query": "What does SOC2 policy require?", "top_k": 2},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200

    body = response.json()
    assert isinstance(body["answer"], str)
    assert len(body["retrieved_chunks"]) >= 1
    assert len(body["citations"]) >= 1
    assert "citation_ref" in body["retrieved_chunks"][0]
