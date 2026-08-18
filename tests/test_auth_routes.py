from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_login_returns_access_token_for_analyst():
    response = client.post(
        "/auth/login",
        json={
            "username": "analyst",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] == 1800


def test_login_returns_access_token_for_developer():
    response = client.post(
        "/auth/login",
        json={
            "username": "developer",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_returns_access_token_for_admin():
    response = client.post(
        "/auth/login",
        json={
            "username": "admin",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_rejects_unknown_user():
    response = client.post(
        "/auth/login",
        json={
            "username": "unknown-user",
        },
    )

    assert response.status_code == 401


def test_login_requires_username():
    response = client.post(
        "/auth/login",
        json={},
    )

    assert response.status_code == 422
