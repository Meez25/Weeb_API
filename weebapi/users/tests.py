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
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], "test@example.com")  # type: ignore[attr-defined]
        self.assertNotIn("password", response.data)  # type: ignore[attr-defined]
        self.assertTrue(User.objects.filter(email="test@example.com").exists())

    def test_create_user_leaves_username_null(self):
        """Signup must not auto-assign a username — the frontend prompts for
        it on first article publication, and NULL is the signal."""
        self.client.post(
            self.url,
            {"email": "blank@example.com", "password": "StrongPass123!"},
        )
        user = User.objects.get(email="blank@example.com")
        self.assertIsNone(user.username)

    def test_create_user_ignores_supplied_username(self):
        """Username is not part of the signup serializer — anything the
        client sends for it is silently dropped, including names already
        taken by another user (no enumeration vector)."""
        User.objects.create_user(  # type: ignore[call-arg]
            email="taken@example.com", password="StrongPass123!", username="Taken"
        )
        response = self.client.post(
            self.url,
            {
                "email": "newbie@example.com",
                "password": "StrongPass123!",
                "username": "Taken",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("username", response.data)  # type: ignore[attr-defined]
        user = User.objects.get(email="newbie@example.com")
        self.assertIsNone(user.username)

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
            username="bob",
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")  # type: ignore[attr-defined]

    def test_me_authenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "me@example.com")  # type: ignore[attr-defined]
        self.assertEqual(response.data["username"], "bob")  # type: ignore[attr-defined]

    def test_me_unauthenticated(self):
        self.client.credentials()  # type: ignore[attr-defined]
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_patch_updates_username(self):
        response = self.client.patch(self.url, {"username": "bobby"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "bobby")

    def test_me_patch_ignores_email_and_password(self):
        """Only username can flow through this endpoint — anything else is
        silently dropped to keep credential changes on their own routes."""
        original_password_hash = self.user.password
        response = self.client.patch(
            self.url,
            {
                "username": "bobby",
                "email": "evil@example.com",
                "password": "Hacked123!",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "me@example.com")
        self.assertEqual(self.user.password, original_password_hash)

    def test_me_patch_unauthenticated(self):
        self.client.credentials()  # type: ignore[attr-defined]
        response = self.client.patch(self.url, {"username": "x"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_patch_without_username_preserves_value(self):
        """A PATCH that doesn't carry the `username` key must NOT wipe the
        existing value — partial-update semantics."""
        response = self.client.patch(self.url, {"email": "ignored@example.com"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "bob")

    def test_me_patch_empty_string_clears_username(self):
        """Empty string is coerced to NULL so the unique constraint allows
        any number of "unset" users."""
        response = self.client.patch(self.url, {"username": ""})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertIsNone(self.user.username)

    def test_me_patch_username_must_be_unique(self):
        """Two users can't share a display name."""
        User.objects.create_user(  # type: ignore[call-arg]
            email="other@example.com", password="StrongPass123!", username="taken"
        )
        response = self.client.patch(self.url, {"username": "taken"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)  # type: ignore[attr-defined]

    def test_me_patch_username_unique_is_case_insensitive(self):
        """Different casings of the same name collide — blocks visual
        impersonation via 'Admin' / 'admin' / 'ADMIN'."""
        User.objects.create_user(  # type: ignore[call-arg]
            email="other@example.com", password="StrongPass123!", username="Admin"
        )
        response = self.client.patch(self.url, {"username": "ADMIN"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)  # type: ignore[attr-defined]

    def test_me_patch_strips_whitespace(self):
        """Surrounding whitespace is normalized away before storage."""
        response = self.client.patch(self.url, {"username": "  bobby  "})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "bobby")

    def test_me_patch_whitespace_only_clears_username(self):
        """Whitespace-only input is treated as 'unset' (NULL), same as ''."""
        response = self.client.patch(self.url, {"username": "   "})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertIsNone(self.user.username)


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
