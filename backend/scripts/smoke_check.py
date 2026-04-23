from fastapi.testclient import TestClient

from app.main import app


def main() -> None:
    with TestClient(app) as client:
        health = client.get("/health")
        assert health.status_code == 200

        login = client.post(
            "/api/auth/login",
            json={"email": "admin@calisto.ai", "password": "password123"},
        )
        assert login.status_code == 200
        token = login.json()["access_token"]

        me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me.status_code == 200

        workspace = client.get("/api/admin/workspace", headers={"Authorization": f"Bearer {token}"})
        assert workspace.status_code == 200

    print("Smoke check passed.")


if __name__ == "__main__":
    main()
