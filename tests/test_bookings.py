from datetime import UTC, datetime, timedelta


def test_create_booking_requires_auth(client, centre_with_test):
    response = client.post(
        "/bookings",
        json={
            "test_id": centre_with_test["test_id"],
            "centre_id": centre_with_test["centre_id"],
            "appointment_at": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
        },
    )
    assert response.status_code == 401


def test_create_and_get_booking(client, auth_headers, centre_with_test):
    appointment_at = (datetime.now(UTC) + timedelta(days=2)).isoformat()
    create_response = client.post(
        "/bookings",
        headers=auth_headers,
        json={
            "test_id": centre_with_test["test_id"],
            "centre_id": centre_with_test["centre_id"],
            "appointment_at": appointment_at,
        },
    )
    assert create_response.status_code == 201
    booking = create_response.json()
    assert booking["status"] == "PENDING"
    assert booking["amount"] == "499.00"

    get_response = client.get(f"/bookings/{booking['id']}", headers=auth_headers)
    assert get_response.status_code == 200
    assert get_response.json()["id"] == booking["id"]


def test_cannot_book_past_appointment(client, auth_headers, centre_with_test):
    response = client.post(
        "/bookings",
        headers=auth_headers,
        json={
            "test_id": centre_with_test["test_id"],
            "centre_id": centre_with_test["centre_id"],
            "appointment_at": (datetime.now(UTC) - timedelta(days=1)).isoformat(),
        },
    )
    assert response.status_code == 409


def test_cannot_access_another_users_booking(client, auth_headers, centre_with_test):
    appointment_at = (datetime.now(UTC) + timedelta(days=2)).isoformat()
    booking_response = client.post(
        "/bookings",
        headers=auth_headers,
        json={
            "test_id": centre_with_test["test_id"],
            "centre_id": centre_with_test["centre_id"],
            "appointment_at": appointment_at,
        },
    )
    booking_id = booking_response.json()["id"]

    client.post(
        "/auth/signup",
        json={
            "email": "other@example.com",
            "full_name": "Other User",
            "password": "password123",
        },
    )
    other_login = client.post(
        "/auth/login",
        json={"email": "other@example.com", "password": "password123"},
    )
    other_headers = {"Authorization": f"Bearer {other_login.json()['access_token']}"}

    response = client.get(f"/bookings/{booking_id}", headers=other_headers)
    assert response.status_code == 403
