def test_signup_and_login(client):
    signup_response = client.post(
        "/auth/signup",
        json={
            "email": "newuser@example.com",
            "full_name": "New User",
            "password": "password123",
        },
    )
    assert signup_response.status_code == 201
    assert signup_response.json()["email"] == "newuser@example.com"

    login_response = client.post(
        "/auth/login",
        json={"email": "newuser@example.com", "password": "password123"},
    )
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()


def test_duplicate_signup_returns_conflict(client):
    payload = {
        "email": "duplicate@example.com",
        "full_name": "Duplicate User",
        "password": "password123",
    }
    client.post("/auth/signup", json=payload)
    response = client.post("/auth/signup", json=payload)
    assert response.status_code == 409


def test_login_with_invalid_credentials(client):
    response = client.post(
        "/auth/login",
        json={"email": "missing@example.com", "password": "password123"},
    )
    assert response.status_code == 401
