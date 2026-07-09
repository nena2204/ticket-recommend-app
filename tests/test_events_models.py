import pytest

from tests.conftest import EventFactory, EventLocationFactory, TicketTypeFactory


pytestmark = pytest.mark.django_db


def test_event_location_string_representation():
    location = EventLocationFactory(city="Ohrid", address="Quay 1", capacity=1200)

    assert str(location) == "Ohrid Quay 1 1200"


def test_event_string_representation():
    event = EventFactory(name="Summer Festival")

    assert str(event) == "Summer Festival"


def test_ticket_type_string_representation():
    ticket_type = TicketTypeFactory(event__name="Summer Festival", name="VIP")

    assert "Summer Festival" in str(ticket_type)
    assert "VIP" in str(ticket_type)
