"""The seed_demo command used by the browser, agent and load tests."""
import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command

from events.management.commands.seed_demo import DEMO_USER, EVENTS
from events.models import Event, TicketType

pytestmark = pytest.mark.django_db


def test_seed_demo_creates_events_tickets_and_user():
    """The command creates every demo event with its ticket types and a working demo user."""
    call_command("seed_demo")

    assert Event.objects.count() == len(EVENTS)
    assert TicketType.objects.count() == sum(len(e[4]) for e in EVENTS)
    username, password = DEMO_USER
    assert get_user_model().objects.get(username=username).check_password(password)


def test_seed_demo_is_idempotent():
    """Running the command twice does not duplicate data."""
    call_command("seed_demo")
    call_command("seed_demo")

    assert Event.objects.count() == len(EVENTS)
    assert TicketType.objects.count() == sum(len(e[4]) for e in EVENTS)
