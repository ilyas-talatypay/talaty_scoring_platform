from fastapi.testclient import TestClient

from api.main import app


def test_health_and_version() -> None:
    client = TestClient(app)

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    response = client.get("/version")
    assert response.status_code == 200
    payload = response.json()
    assert "version" in payload
    assert "git_sha" in payload


def test_schema_endpoints() -> None:
    client = TestClient(app)

    response = client.get("/schemas/v0")
    assert response.status_code == 200
    payload = response.json()
    assert payload.get("version") == "v0"
    assert "schemas" in payload

    response = client.get("/schemas/v0/run_spec")
    assert response.status_code == 200
    assert response.json().get("title") == "RunSpec"
