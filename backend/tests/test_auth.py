def test_login_success(client) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "member@calisto.ai", "password": "member1234"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["role"] == "member"
    assert body["organization_id"] > 0


def test_login_invalid_credentials(client) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "member@calisto.ai", "password": "bad-password"},
    )
    assert response.status_code == 401
