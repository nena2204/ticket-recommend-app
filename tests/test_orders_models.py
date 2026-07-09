from decimal import Decimal

import pytest

from orders.models import TicketOrder
from tests.conftest import OrderItemFactory


pytestmark = pytest.mark.django_db


def test_order_item_subtotal(order_item):
    assert order_item.subtotal() == Decimal("1500.00")


def test_order_total_sums_all_items(order, ticket_type):
    OrderItemFactory(
        order=order,
        event=ticket_type.event,
        ticket_type=ticket_type,
        qty=2,
        unit_price=Decimal("500.00"),
    )
    other = OrderItemFactory(order=order, qty=3, unit_price=Decimal("250.00"))

    assert order.total() == Decimal("1750.00")
    assert other.subtotal() == Decimal("750.00")


def test_ticket_order_can_be_created():
    ticket_order = TicketOrder.objects.create(
        full_name="Ana Test",
        email="ana@example.com",
        phone="+38970111222",
        street="Partizanska",
        street_no="10",
        zip_code="1000",
        city="Skopje",
        total="1500.00",
        items=[{"event": "Test Event", "ticket": "VIP", "qty": 1, "price": 1500}],
    )

    assert ticket_order.pk is not None
    assert ticket_order.status == "created"
