import pytest

from orders.forms import CheckoutForm, ContactForm


@pytest.mark.parametrize(
    "form_class,data",
    [
        (
            CheckoutForm,
            {
                "full_name": "Ana Test",
                "phone": "+38970111222",
                "email": "ana@example.com",
                "street": "Partizanska 10",
                "zip_code": "1000",
                "city": "Skopje",
            },
        ),
        (
            ContactForm,
            {"name": "Ana Test", "email": "ana@example.com", "message": "Hello"},
        ),
    ],
)
def test_form_accepts_valid_data(form_class, data):
    assert form_class(data=data).is_valid()


@pytest.mark.parametrize(
    "form_class,data",
    [
        (CheckoutForm, {"full_name": "", "email": "not-an-email"}),
        (ContactForm, {"name": "", "email": "not-an-email", "message": ""}),
    ],
)
def test_form_rejects_invalid_data(form_class, data):
    form = form_class(data=data)

    assert not form.is_valid()
    assert form.errors
