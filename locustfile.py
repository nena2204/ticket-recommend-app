import random
import re

from locust import HttpUser, between, task


class TicketBrowser(HttpUser):
    """A visitor who browses events and occasionally opens event details."""

    wait_time = between(1, 4)

    def on_start(self):
        self.event_paths = []

    @task(3)
    def open_home_page(self):
        self.client.get("/", name="home")

    @task(2)
    def browse_events(self):
        response = self.client.get("/events/", name="event list")
        if response.ok:
            self.event_paths = list(set(re.findall(r'href="(/events/\d+/)"', response.text)))

    @task(2)
    def open_event_detail(self):
        if not self.event_paths:
            self.browse_events()
        if self.event_paths:
            self.client.get(random.choice(self.event_paths), name="/events/[id]/")

    @task(1)
    def open_contact_page(self):
        # The GET is realistic and safe for repeatable load tests. Form POSTs
        # are intentionally omitted so a load run cannot flood the admin inbox.
        self.client.get("/contact/", name="contact")


# Run against the development server with:
# locust -f locustfile.py --host=http://127.0.0.1:8000
