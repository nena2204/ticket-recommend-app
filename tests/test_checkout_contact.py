import pytest
from django.core import mail
from django.urls import reverse


pytestmark = pytest.mark.django_db


def test_contact_form_submit_accepts_valid_data(client):
    response = client.post(
        reverse("contact"),
        {"name": "Ana Test", "email": "ana@example.com", "message": "Please help."},
    )

    assert response.status_code == 302
    assert response.url == reverse("contact")
    assert len(mail.outbox) == 1
    assert "ana@example.com" in mail.outbox[0].body


def test_contact_form_submit_renders_errors_for_invalid_data(client):
    response = client.post(
        reverse("contact"),
        {"name": "", "email": "invalid", "message": ""},
    )

    assert response.status_code == 200
    assert response.context["form"].errors
    assert len(mail.outbox) == 0
