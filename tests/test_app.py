import json
from app.main import app

def test_health():
    client = app.test_client()
    r = client.get("/health")
    assert r.status_code == 200
    data = r.get_json()
    assert "status" in data

def test_create_validation():
    client = app.test_client()
    r = client.post("/notes", json={})
    assert r.status_code == 400
