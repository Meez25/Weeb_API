from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.test import TestCase

User = get_user_model()


class UserTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        response = self.client.post('/api/users/create/', {
            'email': 'test@example.com',
            'password': 'Motdepasse123!',
            'first_name': 'Jean',
            'last_name': 'Dupont'
        })
        self.assertEqual(response.status_code, 201)

    def test_create_user_password_too_short(self):
        response = self.client.post('/api/users/create/', {
            'email': 'test@example.com',
            'password': '123',
            'first_name': 'Jean',
            'last_name': 'Dupont'
        })
        self.assertEqual(response.status_code, 400)

    def test_create_user_inactive_by_default(self):
        self.client.post('/api/users/create/', {
            'email': 'test@example.com',
            'password': 'Motdepasse123!',
            'first_name': 'Jean',
            'last_name': 'Dupont'
        })
        user = User.objects.get(email='test@example.com')
        self.assertFalse(user.is_active)

    def test_me_unauthenticated(self):
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, 401)

    def test_me_authenticated(self):
        user = User.objects.create_user(
            email='active@example.com',
            password='Motdepasse123!',
            is_active=True
        )
        token = RefreshToken.for_user(user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, 200)
