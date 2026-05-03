from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Contact
from .views import ContactThrottle


class ContactCreateTests(APITestCase):
    url = "/api/contact/"

    valid_data = {
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "+33123456789",
        "email_address": "john@example.com",
        "message": "This is a great message about something positive.",
    }

    def test_create_contact_success(self):
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Contact.objects.filter(email_address="john@example.com").exists())

    def test_create_contact_missing_required_field(self):
        data = {**self.valid_data}
        del data["message"]
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("message", response.data)  # type: ignore[attr-defined]

    def test_create_contact_invalid_email(self):
        data = {**self.valid_data, "email_address": "not-an-email"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_contact_get_not_allowed(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_satisfaction_auto_computed(self):
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        contact = Contact.objects.get(email_address="john@example.com")
        # satisfaction is set by analyze_satisfaction_binary — just check it's not None
        self.assertIsNotNone(contact.satisfaction)

    def test_satisfaction_endpoint_not_exposed(self):
        """Sentiment analysis is internal — no public HTTP endpoint."""
        response = self.client.post("/api/satisfaction/", {"message": "test"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ContactThrottleTests(APITestCase):
    url = "/api/contact/"

    valid_data = {
        "first_name": "Jane",
        "last_name": "Doe",
        "phone_number": "+33123456789",
        "email_address": "jane@example.com",
        "message": "Hello.",
    }

    def setUp(self):
        cache.clear()
        # Monkey-patch the rate so we don't need to fire 10000 requests.
        # SimpleRateThrottle reads `self.rate` in __init__ before falling back
        # to settings, so a class attribute wins per-instance.
        ContactThrottle.rate = "2/hour"
        self.addCleanup(self._restore)

    def _restore(self):
        if "rate" in ContactThrottle.__dict__:
            del ContactThrottle.rate
        cache.clear()

    def test_throttle_returns_429_after_limit(self):
        for _ in range(2):
            response = self.client.post(self.url, self.valid_data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
