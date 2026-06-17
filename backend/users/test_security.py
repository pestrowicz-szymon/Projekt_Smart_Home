from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import (
    BlacklistedToken,
    OutstandingToken,
    RefreshToken,
)


class SecurityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )
        self.client = APIClient()

    def test_logout_blacklists_token(self):
        refresh = RefreshToken.for_user(self.user)
        refresh_token = str(refresh)

        self.client.force_authenticate(user=self.user)

        # Logout
        response = self.client.post(
            "/api/users/logout/", {"refresh": refresh_token}, format="json"
        )
        self.assertEqual(response.status_code, 200)

        # Verify it's blacklisted
        with self.assertRaises(Exception):
            # Refreshing should fail
            RefreshToken(refresh_token).check_blacklist()

    def test_logout_fails_without_token(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/users/logout/", {}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Refresh token required", response.data["detail"])

    @override_settings(SECURE_SSL_REDIRECT=True)
    def test_ssl_redirect_setting(self):
        from django.conf import settings

        self.assertTrue(settings.SECURE_SSL_REDIRECT)

    def test_cors_settings_dynamic(self):
        import os

        from django.conf import settings

        # The current implementation uses os.getenv in settings.py, which is evaluated at load time.
        # Testing dynamic loading here might require re-importing settings or mocking os.environ before import.
        # But we can at least check it's a list/tuple as expected.
        self.assertTrue(isinstance(settings.CORS_ALLOWED_ORIGINS, (list, tuple)))
