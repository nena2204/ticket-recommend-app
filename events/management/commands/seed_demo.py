"""Fill the database with predictable demo data for E2E, agent and load tests.

    python manage.py seed_demo --settings=TicketRecommend.settings_e2e
"""
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from events.models import Event, EventLocation, TicketType

DEMO_USER = ("e2e_user", "E2e-Pass-2026!")

EVENTS = [
    # name, category, days from now, popular, [(ticket name, price)]
    ("E2E Rock Night", "concert", 10, True, [("Regular", "900"), ("VIP", "2500")]),
("E2E Jazz Evening", "concert", 25, False, [("Regular", "700")]),
    ("E2E Summer Festival", "festival", 30, True, [("Day pass", "1500"), ("3-day pass", "3900")]),
    ("E2E Hamlet", "theatre", 5, False, [("Parter", "600")]),
    ("E2E Vardar Derby", "sport", 15, True, [("Tribune North", "300")]),
    ("E2E Philharmonic Gala", "classical", 20, False, [("Standard", "800")]),
]


class Command(BaseCommand):
    help = "Create predictable demo events, ticket types and a demo user."

    def handle(self, *args, **options):
        venue, _ = EventLocation.objects.get_or_create(
            name="E2E Arena", defaults={"city": "Skopje", "address": "Test 1", "capacity": 5000}
        )
        for name, category, days, popular, tickets in EVENTS:
            event, _ = Event.objects.update_or_create(
                name=name,
                defaults={
                    "category": category,
                    "datetime": timezone.now() + timedelta(days=days),
                    "description": f"{name} - demo event for automated tests.",
                    "ticket_price": int(Decimal(tickets[0][1])),
                    "image": "images/IMG_0118.JPG",
                    "location": venue,
                    "is_popular": popular,
                },
            )
            for ticket_name, price in tickets:
                TicketType.objects.update_or_create(
                    event=event, name=ticket_name, defaults={"price": Decimal(price), "qty": 100}
                )

        User = get_user_model()
        username, password = DEMO_USER
        user, _ = User.objects.get_or_create(username=username, defaults={"email": "e2e@example.com"})
        user.set_password(password)
        user.save()
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(EVENTS)} events and user '{username}'."))
