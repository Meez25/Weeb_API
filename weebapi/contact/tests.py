from rest_framework import status
from rest_framework.test import APITestCase

from .models import Contact


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
