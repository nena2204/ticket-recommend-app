# Automated Testing Guide

## Goal

This test project verifies the ticket recommendation and ordering application at
multiple levels. It covers model calculations, forms, Django views, anonymous
session carts, rendered browser journeys, and realistic browsing load.

## Tools

- **pytest-django** provides concise Django unit and integration tests.
- **factory-boy** creates reusable, realistic database records without repeated setup.
- **pytest-cov / coverage.py** measures tested application code and produces reports.
- **Playwright** exercises the real rendered UI in a browser, including JavaScript and forms.
- **Locust** simulates concurrent visitors for performance and load testing.
- **GitHub Actions** runs tests and coverage automatically on pushes and pull requests.

## Strategy and coverage

Unit tests cover `EventLocation`, `Event`, `TicketType`, `Order`,
`OrderItem`, `TicketOrder`, `CheckoutForm`, and `ContactForm`. Integration tests
cover home/event pages, 404 behavior, contact submission, login protection, and
database-backed anonymous cart add/update/remove and session isolation. Playwright
covers home, event ticket details, and contact submission at browser level.
Locust models repeated home, event-list, event-detail, and contact browsing.

E2E tests are marked separately because they require an installed browser. The
default `pytest` command runs the fast unit and integration suite.

## Setup and commands

From the project root in the PyCharm terminal:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
python manage.py migrate
```

Run unit and integration tests:

```powershell
pytest
```

Run coverage and create the browsable `htmlcov/index.html` report:

```powershell
pytest --cov=events --cov=orders --cov=tickets_addons --cov-report=term-missing --cov-report=html
```

Install Chromium once, then run only the browser-level tests:

```powershell
playwright install chromium
pytest -m e2e --browser chromium
```

Start Django and Locust in two terminals:

```powershell
python manage.py runserver
locust -f locustfile.py --host=http://127.0.0.1:8000
```

Open the Locust URL printed in the terminal (normally `http://localhost:8089`),
choose the number of concurrent users and spawn rate, and start the run.

## Suggested division for three team members

1. Maintain model/form unit tests, factories, and coverage analysis.
2. Maintain Django Client integration tests and GitHub Actions.
3. Maintain Playwright journeys, Locust scenarios, and result documentation.

All members should review failures together because a browser or load failure can
reveal a problem below the UI layer. This combination of isolated tests,
cross-component integration, a real browser, concurrent virtual users, coverage,
and CI is substantially broader than basic Django homework testing.

## Screenshots and results

Add course-report evidence here:

- Screenshot of a successful `pytest` run: _TODO_
- Screenshot of the HTML coverage summary: _TODO_
- Screenshot of the Playwright result: _TODO_
- Screenshot/export of the Locust statistics: _TODO_
- Link or screenshot of a successful GitHub Actions run: _TODO_
