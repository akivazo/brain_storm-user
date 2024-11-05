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
    assert isinstance(data, str)

def test_add_user_already_exist(client: FlaskClient):
    response = client.post("/user", json={"name": "John Doe", "password": "secret", "email": "john@example.com"})
    assert response.status_code == 201
    
    # second time
    response = client.post("/user", json={"name": "John Doe", "password": "secret2", "email": "john2@example.com"})
    assert response.status_code == 409
    data = response.get_json()
    assert "error" in data

def test_add_user_missing_field(client: FlaskClient):
    response = client.post("/user", json={"name": "John Doe"})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data

def test_get_user(client: FlaskClient):
    response = create_user(client)
    response = client.get(f"/user/John Doe/secret")
    assert response.status_code == 200
    data = response.get_json()["user"]
    assert data['name'] == "John Doe"
    assert data['email'] == "john@example.com"
    assert data["password"] == "secret"

def test_get_user_wrond_password(client: FlaskClient):
    response = create_user(client)
    response = client.get(f"/user/John Doe/wrond")
    
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data

def test_get_user_no_tags(client: FlaskClient):
    response = client.post("/user", json={"name": "James", "password": "secret", "email": "james@example.com"})
    response = client.get(f"/user/James/secret")
    assert response.status_code == 200
    data = response.get_json()["user"]
    assert data['name'] == "James"
    assert data['email'] == "james@example.com"
    assert data["password"] == "secret"

def test_get_nonexistent_user(client: FlaskClient):
    response = client.get("/user/000000000000000000000000/secret")
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data

def test_delete_user(client: FlaskClient):
    response = create_user(client)
    response = client.get(f"/user/John Doe/secret")
    assert response.status_code == 200
    response = client.delete(f"/user/John Doe/secret")
    assert response.status_code == 204
    response = client.get(f"/user/John Doe/secret")
    assert response.status_code == 404

def test_deleted_wrong_user(client: FlaskClient):
    response = create_user(client)
    response = client.get(f"/user/John Doe/secret")
    assert response.status_code == 200
    response = client.delete(f"/user/John duck/secret")
    assert response.status_code == 404
    response = client.delete(f"/user/John Doe/wrong")
    assert response.status_code == 404

def test_is_user_exist(client: FlaskClient):
    response = client.post("/user", json={"name": "James", "password": "secret", "email": "james@example.com"})
    assert response.status_code == 201
    response = client.get("/user_exist/James") # same user again
    assert response.get_json() == "Y"
    response = client.get("/user_exist/John") # different user
    assert response.get_json() == "N"

def test_favorites(client: FlaskClient):
    create_user(client)

    response = client.get(f"/user/John Doe/secret")
    user = response.get_json()["user"]

    assert user["favorites"] == []

    response = client.post("/favorite/John Doe/id1")
    assert response.status_code == 200

    response = client.post("/favorite/John Doe/id2")
    assert response.status_code == 200

    response = client.get(f"/user/John Doe/secret")
    user = response.get_json()["user"]

    assert user["favorites"] == ["id1", "id2"]

    response = client.delete("/favorite/John Doe/id2")
    assert response.status_code == 200

    response = client.get(f"/user/John Doe/secret")
    user = response.get_json()["user"]

    assert user["favorites"] == ["id1"]