from datetime import timedelta
from decimal import Decimal

import factory
import pytest
from django.utils import timezone

from events.models import Event, EventLocation, TicketType
from orders.models import Order, OrderItem


class EventLocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EventLocation

    city = "Skopje"
    address = factory.Sequence(lambda n: f"Test Street {n}")
    name = factory.Sequence(lambda n: f"Test Venue {n}")
    capacity = 500


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event

    name = factory.Sequence(lambda n: f"Test Event {n}")
    category = "concert"
    datetime = factory.LazyFunction(lambda: timezone.now() + timedelta(days=7))
    description = "An event created by the automated test suite."
    ticket_price = 1000
    image = "images/test-event.jpg"
    location = factory.SubFactory(EventLocationFactory)
    is_popular = True


class TicketTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TicketType

    event = factory.SubFactory(EventFactory)
    name = factory.Sequence(lambda n: f"Regular {n}")
    price = Decimal("750.00")
    qty = 100


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    session_key = factory.Sequence(lambda n: f"test-session-{n}")
    status = "cart"


class OrderItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderItem

    order = factory.SubFactory(OrderFactory)
    ticket_type = factory.SubFactory(TicketTypeFactory)
    event = factory.SelfAttribute("ticket_type.event")
    qty = 2
    unit_price = Decimal("750.00")


@pytest.fixture(autouse=True)
def test_email_backend(settings):
    """Never let an automated test connect to the configured SMTP account."""
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"


@pytest.fixture
def location():
    return EventLocationFactory()


@pytest.fixture
def event():
    return EventFactory()


@pytest.fixture
def ticket_type(event):
    return TicketTypeFactory(event=event)


@pytest.fixture
def order():
    return OrderFactory()


@pytest.fixture
def order_item(order, ticket_type):
    return OrderItemFactory(order=order, ticket_type=ticket_type, event=ticket_type.event)
