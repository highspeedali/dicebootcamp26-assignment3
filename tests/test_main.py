from fastapi.testclient import TestClient

from main import app, items

client = TestClient(app)


def setup_function():
    items.clear()


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "version" in response.json()


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "ok"

def test_get_item_not_found():
    response = client.get("/items/2")
    assert response.status_code == 404
    assert response.json() == {"detail": "Item 2 not found"}

