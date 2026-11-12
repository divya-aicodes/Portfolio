import sqlite3

import pytest

from app import create_app


@pytest.fixture()
def application(tmp_path):
    return create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret-key",
            "DATABASE": str(tmp_path / "test.sqlite3"),
            "RATE_LIMIT_ENABLED": False,
        }
    )


@pytest.fixture()
def client(application):
    return application.test_client()


def get_csrf_token(client):
    client.get("/")
    with client.session_transaction() as session:
        return session["csrf_token"]


def test_home_page_contains_verified_profile(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Divya Jain" in response.data
    assert b"Blockwise.AI" in response.data
    assert b"Vita AI" in response.data
    assert "Virasā".encode() in response.data
    assert response.data.index("Virasā".encode()) < response.data.index(b"Vita AI")
    assert b"Aetherion AQI" not in response.data
    assert b"TECHNICAL SKILLS" in response.data
    assert b"Python Lab" not in response.data
    assert b'id="hypercube-canvas"' in response.data
    assert b'class="section-rail"' in response.data
    assert b'class="brand-monogram"' in response.data
    assert b"images/divya-hero-cutout.png" in response.data
    assert b"https://virasa-umber.vercel.app" in response.data


def test_profile_api_proves_python_backend(client):
    response = client.get("/api/profile")
    assert response.status_code == 200
    assert response.json["served_by"] == "Flask"
    assert response.json["project_count"] == 3
    assert response.json["python_project_count"] == 2


def test_contact_submission_is_persisted(application, client):
    response = client.post(
        "/api/contact",
        json={
            "csrf_token": get_csrf_token(client),
            "name": "Ada Lovelace",
            "email": "ada@example.com",
            "message": "I would like to discuss a thoughtful collaboration.",
            "website": "",
        },
    )
    assert response.status_code == 201

    with sqlite3.connect(application.config["DATABASE"]) as database:
        saved = database.execute("SELECT name, email FROM messages").fetchone()
    assert saved == ("Ada Lovelace", "ada@example.com")


def test_contact_rejects_invalid_input(client):
    response = client.post(
        "/api/contact",
        json={
            "csrf_token": get_csrf_token(client),
            "name": "A",
            "email": "not-an-email",
            "message": "short",
            "website": "",
        },
    )
    assert response.status_code == 422
    assert set(response.json["fields"]) == {"name", "email", "message"}


def test_contact_rejects_missing_csrf(client):
    response = client.post(
        "/api/contact",
        json={"name": "Ada", "email": "ada@example.com", "message": "A sufficiently long message."},
    )
    assert response.status_code == 403


def test_security_headers_are_present(client):
    response = client.get("/")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json == {"service": "divya-portfolio", "status": "ok"}
