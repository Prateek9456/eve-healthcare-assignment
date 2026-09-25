from datetime import UTC, datetime, timedelta


def _create_pending_booking(client, auth_headers, centre_with_test) -> int:
    response = client.post(
        "/bookings",
        headers=auth_headers,
        json={
            "test_id": centre_with_test["test_id"],
            "centre_id": centre_with_test["centre_id"],
            "appointment_at": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
        },
    )
    return response.json()["id"]


def test_simulated_payment_success(client, auth_headers, centre_with_test):
    booking_id = _create_pending_booking(client, auth_headers, centre_with_test)
    payment_response = client.post(
        "/payments",
        headers=auth_headers,
        json={"booking_id": booking_id, "simulate_success": True},
    )
    assert payment_response.status_code == 201
    assert payment_response.json()["status"] == "SUCCESS"

    booking_response = client.get(f"/bookings/{booking_id}", headers=auth_headers)
    assert booking_response.json()["status"] == "CONFIRMED"


def test_simulated_payment_failure(client, auth_headers, centre_with_test):
    booking_id = _create_pending_booking(client, auth_headers, centre_with_test)
    payment_response = client.post(
        "/payments",
        headers=auth_headers,
        json={"booking_id": booking_id, "simulate_success": False},
    )
    assert payment_response.status_code == 201
    assert payment_response.json()["status"] == "FAILED"

    booking_response = client.get(f"/bookings/{booking_id}", headers=auth_headers)
    assert booking_response.json()["status"] == "FAILED"


def test_webhook_is_idempotent(client, auth_headers, centre_with_test):
    booking_id = _create_pending_booking(client, auth_headers, centre_with_test)
    payload = {
        "event_id": "evt_12345",
        "booking_id": booking_id,
        "status": "SUCCESS",
        "amount": "499.00",
    }

    first = client.post("/payments/webhook", json=payload)
    second = client.post("/payments/webhook", json=payload)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["id"] == second.json()["id"]


def test_payment_for_invalid_booking(client, auth_headers):
    response = client.post(
        "/payments",
        headers=auth_headers,
        json={"booking_id": 99999, "simulate_success": True},
    )
    assert response.status_code == 404
