from main import app, items
from fastapi.testclient import TestClient

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


def test_create_item():
    response = client.post("/items/1", json={"name": "Test Item", "price": 10.0})
    assert response.status_code == 201
    assert response.json() == {"message": "Item created successfully"}
    assert items[1] == {"name": "Test Item", "price": 10.0}


def test_get_item():
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json() == {"name": "Test Item", "price": 10.0}
    assert items[1] == {"name": "Test Item", "price": 10.0}


def test_get_item_not_found():
    response = client.get("/items/2")
    assert response.status_code == 404
    assert response.json() == {"detail": "Item 2 not found"}


def test_create_item_already_exists():
    response = client.post("/items/1", json={"name": "Test Item", "price": 10.0})
    assert response.status_code == 400
    assert response.json() == {"detail": "Item already exists"}
    assert items[1] == {"name": "Test Item", "price": 10.0}


def test_create_item_invalid_json():
    response = client.post("/items/1", json="invalid json")
    assert response.status_code == 422
    assert response.json() == {"detail": "Invalid JSON"}
    assert items[1] == {"name": "Test Item", "price": 10.0}


def test_create_item_invalid_item_id():
    response = client.post("/items/invalid", json={"name": "Test Item", "price": 10.0})
    assert response.status_code == 422
    assert response.json() == {"detail": "Invalid item ID"}
    assert items[1] == {"name": "Test Item", "price": 10.0}
