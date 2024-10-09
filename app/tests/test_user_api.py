import pytest
from flask import Flask
from flask.testing import FlaskClient
from mongomock import MongoClient
from ..user_api import server, set_mongo_client

@pytest.fixture
def client():
    # Create a mock MongoDB client
    mock_mongo_client = MongoClient()
    set_mongo_client(mock_mongo_client)
    server.config['TESTING'] = True
    # Set up Flask test client
    client = server.test_client()
    yield client
    mock_mongo_client.close()

def create_user(client: FlaskClient):
    return client.post("/user", json={"name": "John Doe", "password": "secret", "email": "john@example.com", "tags": ["tag1", "tag2"]})

def test_root(client: FlaskClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.data == b"User Api"

def test_add_user(client: FlaskClient):
    response = create_user(client)
    assert response.status_code == 201
    data = response.get_json()
    assert isinstance(data["id"], str) #id

def test_add_user_missing_field(client: FlaskClient):
    response = client.post("/user", json={"name": "John Doe"})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data

def test_get_user(client: FlaskClient):
    response = create_user(client)
    user_id = response.get_json()["id"]
    response = client.get(f"/user/{user_id}/secret")
    assert response.status_code == 200
    data = response.get_json()["user"]
    assert data['name'] == "John Doe"
    assert data['email'] == "john@example.com"
    assert data["tags"] == ["tag1", "tag2"]
    assert data["password"] == "secret"

def test_get_user_wrond_password(client: FlaskClient):
    response = create_user(client)
    user_id = response.get_json()["id"]
    response = client.get(f"/user/{user_id}/wrond")
    
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data

def test_get_user_no_tags(client: FlaskClient):
    response = client.post("/user", json={"name": "James", "password": "secret", "email": "james@example.com"})
    user_id = response.get_json()["id"]
    response = client.get(f"/user/{user_id}/secret")
    assert response.status_code == 200
    data = response.get_json()["user"]
    assert data['name'] == "James"
    assert data['email'] == "james@example.com"
    assert data["tags"] == []
    assert data["password"] == "secret"

def test_get_nonexistent_user(client: FlaskClient):
    response = client.get("/user/000000000000000000000000/secret")
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data

def test_delete_user(client: FlaskClient):
    response = create_user(client)
    user_id = response.get_json()
    response = client.delete(f"/user/{user_id}")
    assert response.status_code == 204
    response = client.get(f"/user/{user_id}/secret")
    assert response.status_code == 404
