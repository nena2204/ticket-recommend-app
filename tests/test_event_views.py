import pytest
from django.urls import reverse


pytestmark = pytest.mark.django_db


def test_home_page_loads_and_displays_event(client, event):
    response = client.get(reverse("home"))

    assert response.status_code == 200
    assert event.name.encode() in response.content


def test_event_list_loads_and_displays_event(client, event):
    response = client.get(reverse("events"))

    assert response.status_code == 200
    assert event.name.encode() in response.content


def test_event_detail_loads_existing_event(client, event, ticket_type):
    response = client.get(reverse("event_detail", args=[event.pk]))

    assert response.status_code == 200
    assert response.context["event"] == event
    assert ticket_type.name.encode() in response.content


def test_event_detail_returns_404_for_unknown_id(client):
    response = client.get(reverse("event_detail", args=[999999]))

    assert response.status_code == 404
