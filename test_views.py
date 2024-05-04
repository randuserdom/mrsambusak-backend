from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_register_user():
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword",
    }
    
    response = client.post("/register", json=user_data)
    assert response.status_code == 201
    assert response.json() == {"message": "User created successfully"}
