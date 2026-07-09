import pytest
from django.urls import reverse

from orders.models import Order, OrderItem


pytestmark = pytest.mark.django_db


def test_cart_add_returns_json_and_creates_anonymous_cart(client, ticket_type):
    response = client.post(
        reverse("cart_add"),
        {"ticket_type_id": ticket_type.pk, "qty": 2},
    )

    assert response.status_code == 200
    assert response.json() == {"ok": True, "count": 2, "total": 1500.0}
    cart = Order.objects.get(session_key=client.session.session_key, status="cart")
    assert cart.items.get().qty == 2


def test_cart_update_changes_quantity(client, ticket_type):
    client.post(reverse("cart_add"), {"ticket_type_id": ticket_type.pk, "qty": 1})
    item = OrderItem.objects.get()

    response = client.post(reverse("cart_update"), {"item_id": item.pk, "qty": 4})

    assert response.status_code == 302
    item.refresh_from_db()
    assert item.qty == 4


def test_cart_remove_deletes_item(client, ticket_type):
    client.post(reverse("cart_add"), {"ticket_type_id": ticket_type.pk, "qty": 1})
    item = OrderItem.objects.get()

    response = client.get(reverse("cart_remove", args=[item.pk]))

    assert response.status_code == 302
    assert not OrderItem.objects.filter(pk=item.pk).exists()


def test_checkout_requires_login(client):
    response = client.get(reverse("checkout"))

    assert response.status_code == 302
    assert response.url.startswith(reverse("login"))


def test_anonymous_carts_are_isolated_by_session(ticket_type, client):
    second_client = client.__class__()
    client.post(reverse("cart_add"), {"ticket_type_id": ticket_type.pk, "qty": 1})
    second_client.post(reverse("cart_add"), {"ticket_type_id": ticket_type.pk, "qty": 3})

    first_cart = Order.objects.get(session_key=client.session.session_key)
    second_cart = Order.objects.get(session_key=second_client.session.session_key)
    assert first_cart.pk != second_cart.pk
    assert first_cart.items.get().qty == 1
    assert second_cart.items.get().qty == 3
