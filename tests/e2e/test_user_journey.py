import os

import pytest
from django.urls import reverse

from tests.conftest import EventFactory, TicketTypeFactory


# pytest-playwright can run with an active event loop while pytest-django is
# preparing the temporary test database. These E2E tests are isolated and run
# against Django's test database, so allowing Django's sync test setup here is
# safe for this browser-test module.
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

# These tests drive a real browser and rendered UI. They complement, rather
# than duplicate, the faster Django Client integration tests.
pytestmark = [pytest.mark.e2e, pytest.mark.django_db(transaction=True)]


def test_user_opens_home_page_and_sees_event(page, live_server):
    event = EventFactory(name="Playwright Concert")

    page.goto(f"{live_server.url}{reverse('home')}")

    assert page.get_by_text(event.name).first.is_visible()


def test_user_opens_event_detail_and_sees_ticket_information(page, live_server):
    event = EventFactory(name="Browser Test Festival")
    ticket_type = TicketTypeFactory(event=event, name="Browser VIP")

    page.goto(f"{live_server.url}{reverse('event_detail', args=[event.pk])}")

    assert page.get_by_role("heading", name=event.name).is_visible()
    assert page.get_by_text(ticket_type.name).is_visible()
    assert page.get_by_text("Tickets", exact=True).is_visible()


def test_user_submits_contact_form(page, live_server):
    page.goto(f"{live_server.url}{reverse('contact')}")
    page.get_by_label("Your Name:").fill("Playwright User")
    page.get_by_label("Your email:").fill("browser@example.com")
    page.get_by_label("Your message:").fill("Browser-level contact test")

    page.get_by_role("button", name="Send").click()

    page.wait_for_url(f"{live_server.url}{reverse('contact')}")
    assert page.get_by_label("Your email:").is_visible()
