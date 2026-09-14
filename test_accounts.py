def test_create_account(client):
    response = client.post("/accounts", json={"owner_name": "Boom Boom", "currency": "BOM"})
    assert response.status_code == 201
    body=response.json()
    assert body['owner_name'] == "Boom Boom"
    assert body['currency'] == "BOM"
    assert body["balance"] == "0.0000"

def test_get_account(client):
    created = client.post("/accounts", json={"owner_name": "Boom Boom", "currency": "BOM"}).json()
    response = client.get(f"/accounts/{created['id']}")
    assert response.status_code == 200
    assert response.json()["owner_name"] == "Boom Boom"


def test_get_account_not_found(client):
    response = client.get("/accounts/999999")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_list_accounts(client):
    client.post("/accounts", json={"owner_name": "Carl", "currency": "GBP"})
    client.post("/accounts", json={"owner_name": "Dana", "currency": "GBP"})
    response = client.get("/accounts")
    names = [a["owner_name"] for a in response.json()]
    assert "Carl" in names and "Dana" in names


def test_update_account(client):
    created = client.post("/accounts", json={"owner_name": "Eve", "currency": "USD"}).json()
    response = client.patch(f"/accounts/{created['id']}", json={"owner_name": "Eve Updated"})
    assert response.status_code == 200
    assert response.json()["owner_name"] == "Eve Updated"


def test_update_account_not_found(client):
    response = client.patch("/accounts/999999", json={"owner_name": "Ghost"})
    assert response.status_code == 404


def test_delete_account(client):
    created = client.post("/accounts", json={"owner_name": "Frank", "currency": "USD"}).json()
    response = client.delete(f"/accounts/{created['id']}")
    assert response.status_code == 204
    assert client.get(f"/accounts/{created['id']}").status_code == 404


def test_delete_account_not_found(client):
    assert client.delete("/accounts/999999").status_code == 404


def test_create_account_validation_error(client):
    response = client.post("/accounts", json={"owner_name": "Bad", "currency": 123})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_create_account_conflict(client):
    client.post("/accounts", json={"owner_name": "Zed", "currency": "INR"})
    response = client.post("/accounts", json={"owner_name": "Zed", "currency": "INR"})
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CONFLICT"