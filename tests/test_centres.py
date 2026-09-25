def test_create_and_list_centres(client):
    create_response = client.post(
        "/centres",
        json={
            "name": "City Diagnostics",
            "location": "Bengaluru",
            "tests": [
                {"name": "Lipid Profile", "price": "799.00"},
                {"name": "Thyroid Panel", "price": "999.00"},
            ],
        },
    )
    assert create_response.status_code == 201
    assert len(create_response.json()["tests"]) == 2

    list_response = client.get("/centres?page=1&page_size=10")
    assert list_response.status_code == 200
    data = list_response.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


def test_get_centre_not_found(client):
    response = client.get("/centres/99999")
    assert response.status_code == 404
