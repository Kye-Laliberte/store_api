import pytest
from pydantic import ValidationError

import models.ordermodels as order_models
import models.sqlAmodels as models
from core.config import Settings


def test_jwt_secret_requires_at_least_32_bytes():
    with pytest.raises(ValidationError):
        Settings(DATABASE_URL="sqlite://", JWT_SECRET_KEY="too-short")


def test_home_and_item_endpoints(client, make_user, auth_headers):
    assert client.get("/").status_code == 200

    response = client.get("/items/get_all")
    assert response.status_code == 200
    assert response.json() == []

    item_payload = {
        "name": "Desk Lamp",
        "description": "Adjustable lamp",
        "quantity": 12,
        "price": 19.95,
    }
    assert client.post("/items/add_item", json=item_payload).status_code == 401
    assert client.post(
        "/items/add_item",
        json=item_payload,
        headers={"Authorization": "Bearer invalid-token"},
    ).status_code == 401

    regular_headers = auth_headers(make_user())
    assert client.post(
        "/items/add_item", json=item_payload, headers=regular_headers
    ).status_code == 403
    admin_headers = auth_headers(
        make_user(email="inventory-admin@example.com", is_admin=True)
    )
    response = client.post(
        "/items/add_item",
        json=item_payload,
        headers=admin_headers,
    )
    assert response.status_code == 201
    item_id = response.json()["id"]

    response = client.put(
        f"/items/{item_id}/update",
        json={"description": "Updated lamp", "quantity": 9, "price": 21.5},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["quantity"] == 9

    response = client.get(f"/items/{item_id}/details")
    assert response.status_code == 200
    assert response.json()["description"] == "Updated lamp"

    response = client.get("/items/get_all")
    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [item_id]


def test_user_endpoints(client, db_session, make_user, auth_headers):
    response = client.post(
        "/users/addUser",
        json={"email": "new@example.com", "password": "a-long-test-password"},
    )
    assert response.status_code == 201
    user_id = response.json()["id"]
    user = db_session.query(models.User).filter_by(id=user_id).one()
    headers = auth_headers(user)

    assert client.get("/users/new@example.com/RetrievebyEmail").status_code == 401
    response = client.get("/users/new@example.com/RetrievebyEmail", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == user_id

    assert client.get("/users/getAll", headers=headers).status_code == 403
    admin_user = make_user(email="admin@example.com", is_admin=True)
    admin_headers = auth_headers(admin_user)
    response = client.get("/users/getAll", headers=admin_headers)
    assert response.status_code == 200
    assert any(user["id"] == user_id for user in response.json())

    assert client.post(
        f"/users/{user_id}/grant_admin", headers=headers
    ).status_code == 403
    response = client.post(
        f"/users/{user_id}/grant_admin", headers=admin_headers
    )
    assert response.status_code == 200
    assert response.json()["is_admin"] is True

    response = client.get(f"/users/{user_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "new@example.com"

    response = client.post(
        "/users/login",
        json={"email": "new@example.com", "password": "a-long-test-password"},
    )
    assert response.status_code == 200
    assert response.json()["access_token"]
    admin_login = client.post(
        "/users/login",
        json={"email": admin_user.email, "password": "correct-horse-battery"},
    )
    assert admin_login.status_code == 200
    assert admin_login.json()["is_admin"] is True

    response = client.post(
        "/users/login",
        json={"email": "missing@example.com", "password": "a-long-test-password"},
    )
    assert response.status_code == 401

    other_user = make_user(email="other@example.com")
    other_headers = auth_headers(other_user)
    assert client.get(f"/users/{user_id}", headers=other_headers).status_code == 403
    assert (
        client.get("/users/new@example.com/RetrievebyEmail", headers=other_headers).status_code
        == 403
    )
    response = client.put(
        f"/users/{user.id}/status",
        params={"status": "inactive"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["user_status"] == "inactive"


def test_cart_endpoints(client, make_user, make_item, auth_headers):
    user = make_user()
    other_user = make_user(email="other@example.com")
    item = make_item()
    headers = auth_headers(user)

    assert client.get("/carts/").status_code == 200
    assert client.get("/carts/getallcarts", headers=headers).status_code == 403
    admin_headers = auth_headers(make_user(email="admin@example.com", is_admin=True))
    response = client.get("/carts/getallcarts", headers=admin_headers)
    assert response.status_code == 200
    assert response.json() == []

    response = client.post(f"/carts/{user.id}/newcart", headers=headers)
    assert response.status_code == 201
    cart_id = response.json()["id"]

    response = client.get(f"/carts/{user.id}/viewcart/{cart_id}", headers=headers)
    assert response.status_code == 200
    assert response.json() == []
    assert (
        client.get(
            f"/carts/{user.id}/viewcart/{cart_id}",
            headers=auth_headers(other_user),
        ).status_code
        == 403
    )

    response = client.post(
        f"/carts/{user.id}/additem/{cart_id}",
        json={"item_id": item.id, "quantity": 2},
        headers=headers,
    )
    assert response.status_code == 201
    assert response.json()["totalprice"] == 8.5

    response = client.get(f"/carts/{user.id}/viewcart/{cart_id}", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = client.delete(
        f"/carts/{cart_id}/{user.id}/removeitem/{item.id}", headers=headers
    )
    assert response.status_code == 200
    assert response.json() == {"item_id": item.id, "quantity": 2}

    response = client.post(
        f"/carts/{user.id}/additem/{cart_id}",
        json={"item_id": item.id, "quantity": 1},
        headers=headers,
    )
    assert response.status_code == 201

    response = client.delete(f"/carts/{user.id}/dropCart/{cart_id}", headers=headers)
    assert response.status_code == 204


def test_order_endpoints(client, db_session, make_user, make_item, make_cart, auth_headers):
    user = make_user()
    other_user = make_user(email="other@example.com")
    item = make_item(quantity=8)
    cart = make_cart(user)
    db_session.add(models.CartItem(cart_id=cart.id, item_id=item.id, quantity=3))
    db_session.commit()
    headers = auth_headers(user)

    assert client.get("/orders/").status_code == 200
    assert client.get("/orders/getallorders").status_code == 401
    assert client.get("/orders/getallorders", headers=headers).status_code == 403
    admin_headers = auth_headers(make_user(email="admin@example.com", is_admin=True))
    response = client.get("/orders/getallorders", headers=admin_headers)
    assert response.status_code == 200
    assert response.json() == []

    response = client.post(
        f"/orders/{user.id}/orderCart/{cart.id}", headers=headers
    )
    assert response.status_code == 201
    order_id = response.json()["id"]
    assert response.json()["number_of_items"] == 3

    for path in (
        f"/orders/{user.id}/vieworders",
        f"/orders/{user.id}/TodayOrders",
        f"/orders/{user.id}/weekOrder",
        "/orders/getallorders",
    ):
        response = client.get(
            path,
            headers=admin_headers if path == "/orders/getallorders" else headers,
        )
        assert response.status_code == 200, response.text
        assert len(response.json()) == 1

    assert (
        client.get(
            f"/orders/{user.id}/vieworders",
            headers=auth_headers(other_user),
        ).status_code
        == 403
    )

    for path in (
        f"/orders/{order_id}/details",
        f"/orders/{user.id}/vieworderdetails",
    ):
        response = client.get(path, headers=headers)
        assert response.status_code == 200, response.text
        assert response.json()[0]["item_id"] == item.id

    order = db_session.query(order_models.Order).filter_by(id=order_id).one()
    assert order.order_date is not None