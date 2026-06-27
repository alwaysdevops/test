import pytest

from app import create_app


@pytest.fixture()
def client(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "DATABASE": str(tmp_path / "test.db"),
        }
    )
    return app.test_client()


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_register_user_with_json(client):
    response = client.post(
        "/register",
        json={
            "name": "Asha Rao",
            "email": "asha@example.com",
            "event": "Cloud Workshop",
        },
    )

    assert response.status_code == 201
    assert response.get_json()["message"] == "Registration successful"

    users = client.get("/api/users").get_json()
    assert len(users) == 1
    assert users[0]["email"] == "asha@example.com"


def test_register_user_rejects_duplicate_email(client):
    payload = {
        "name": "Asha Rao",
        "email": "asha@example.com",
        "event": "Cloud Workshop",
    }

    assert client.post("/register", json=payload).status_code == 201
    duplicate = client.post("/register", json=payload)

    assert duplicate.status_code == 409
    assert "already registered" in duplicate.get_json()["errors"][0]


def test_register_user_rejects_invalid_payload(client):
    response = client.post("/register", json={"name": "", "email": "bad", "event": ""})

    assert response.status_code == 400
    assert len(response.get_json()["errors"]) == 3
