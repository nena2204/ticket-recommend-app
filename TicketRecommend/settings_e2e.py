"""Settings for browser tests and load tests against a real running server.

Uses a separate, throw-away SQLite database filled by `manage.py seed_demo`,
and prints e-mails to the console instead of sending them.
"""
from .settings import *  # noqa: F401,F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "e2e_db.sqlite3",  # noqa: F405
    }
}
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
