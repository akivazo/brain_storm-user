import pytest
from flask import Flask
from flask.testing import FlaskClient
from mongomock import MongoClient
from ..user_api import server, set_mongo_client

@pytest.fixture(scope="module")
def mongo_client():
    return MongoClient()

@pytest.fixture(scope="module")
def client(mongo_client):
    set_mongo_client(mongo_client)
    server.config['TESTING'] = True
    with server.test_client() as client:
        yield client

def test_root(client: FlaskClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.data == b"User Storage"

def test_add_user(client: FlaskClient):
    response = client.post("/user", json={"name": "John Doe", "email": "john@example.com", "tags": ["tag1", "tag2"]})
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, str) #id

def test_add_user_missing_field(client: FlaskClient):
    response = client.post("/user", json={"name": "John Doe"})
    assert response.status_code == 400
    data = response.get_json()
    assert data == 'Missing or empty field: email'

def test_get_user(client: FlaskClient):
    response = client.post("/user", json={"name": "Jane Doe", "email": "jane@example.com", "tags": ["tag1", "tag2"]})
    user_id = response.get_json()
    response = client.get(f"/user/{user_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == "Jane Doe"
    assert data['email'] == "jane@example.com"
    assert data["tags"] == ["tag1", "tag2"]

def test_get_user_no_tags(client: FlaskClient):
    response = client.post("/user", json={"name": "James", "email": "james@example.com"})
    user_id = response.get_json()
    response = client.get(f"/user/{user_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == "James"
    assert data['email'] == "james@example.com"
    assert data["tags"] == []

def test_get_nonexistent_user(client: FlaskClient):
    response = client.get("/user/000000000000000000000000")
    assert response.status_code == 404
    data = response.get_json()
    assert data == "User with id '000000000000000000000000' was not found"

def test_delete_user(client: FlaskClient):
    response = client.post("/user", json={"name": "John Smith", "email": "john.smith@example.com"})
    user_id = response.get_json()
    response = client.delete(f"/user/{user_id}")
    assert response.status_code == 204
    response = client.get(f"/user/{user_id}")
    assert response.status_code == 404
