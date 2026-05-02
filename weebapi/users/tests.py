from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User


class UserCreateTests(APITestCase):
    url = "/api/users/create/"

    def test_create_user_success(self):
        data = {
            "email": "test@example.com",
            "password": "StrongPass123!",
            "first_name": "Alice",
            "last_name": "Doe",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], "test@example.com")  # type: ignore[attr-defined]
        self.assertNotIn("password", response.data)  # type: ignore[attr-defined]
        self.assertTrue(User.objects.filter(email="test@example.com").exists())

    def test_create_user_weak_password(self):
        data = {"email": "test@example.com", "password": "123"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)  # type: ignore[attr-defined]

    def test_create_user_duplicate_email(self):
        User.objects.create_user(email="dupe@example.com", password="StrongPass123!")  # type: ignore[call-arg]
        data = {"email": "dupe@example.com", "password": "StrongPass123!"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_missing_email(self):
        data = {"password": "StrongPass123!"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserMeTests(APITestCase):
    url = "/api/users/me/"

    def setUp(self):
        self.user = User.objects.create_user(  # type: ignore[call-arg]
            email="me@example.com",
            password="StrongPass123!",
            first_name="Bob",
            last_name="Smith",
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")  # type: ignore[attr-defined]

    def test_me_authenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "me@example.com")  # type: ignore[attr-defined]

    def test_me_unauthenticated(self):
        self.client.credentials()  # type: ignore[attr-defined]
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class JWTTokenTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(  # type: ignore[call-arg]
            email="jwt@example.com", password="StrongPass123!"
        )

    def test_obtain_token(self):
        response = self.client.post(
            "/api/token/",
            {"email": "jwt@example.com", "password": "StrongPass123!"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)  # type: ignore[attr-defined]
        self.assertIn("refresh", response.data)  # type: ignore[attr-defined]

    def test_obtain_token_wrong_password(self):
        response = self.client.post(
            "/api/token/",
            {"email": "jwt@example.com", "password": "wrongpassword"},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token(self):
        tokens = self.client.post(
            "/api/token/",
            {"email": "jwt@example.com", "password": "StrongPass123!"},
        ).data  # type: ignore[attr-defined]
        response = self.client.post("/api/token/refresh/", {"refresh": tokens["refresh"]})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)  # type: ignore[attr-defined]

    def test_verify_token(self):
        tokens = self.client.post(
            "/api/token/",
            {"email": "jwt@example.com", "password": "StrongPass123!"},
        ).data  # type: ignore[attr-defined]
        response = self.client.post("/api/token/verify/", {"token": tokens["access"]})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_inactive_user_cannot_obtain_token(self):
        inactive = User.objects.create_user(  # type: ignore[call-arg]
            email="inactive@example.com", password="StrongPass123!"
        )
        inactive.is_active = False
        inactive.save()
        response = self.client.post(
            "/api/token/",
            {"email": "inactive@example.com", "password": "StrongPass123!"},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
