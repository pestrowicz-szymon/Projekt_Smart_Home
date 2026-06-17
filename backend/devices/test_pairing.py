from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Gateway, Home

User = get_user_model()


class GatewayPairingTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.force_authenticate(user=self.user)
        # Assuming MFA is verified for these tests if IsMFAVerified is used
        # If IsMFAVerified checks a session variable, we might need to set it.
        # For now, let's see if it passes without it or if we need to mock it.
        self.home = Home.objects.create(name="Test Home", owner=self.user)
        self.gateway = Gateway.objects.create(
            hardware_id="test-gateway",
            pairing_code="123456",
            status=Gateway.Status.ONLINE,
        )

    def test_claim_gateway_success(self):
        url = reverse("gateway-claim")
        data = {
            "hardware_id": "test-gateway",
            "home_id": self.home.id,
            "pairing_code": "123456",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.gateway.refresh_from_db()
        self.assertEqual(self.gateway.home, self.home)
        self.assertIsNone(self.gateway.pairing_code)

    def test_claim_gateway_invalid_pin(self):
        url = reverse("gateway-claim")
        data = {
            "hardware_id": "test-gateway",
            "home_id": self.home.id,
            "pairing_code": "wrong",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.gateway.refresh_from_db()
        self.assertIsNone(self.gateway.home)
        self.assertEqual(self.gateway.pairing_code, "123456")

    def test_claim_gateway_missing_fields(self):
        url = reverse("gateway-claim")
        data = {
            "hardware_id": "test-gateway",
            "home_id": self.home.id,
            # missing pairing_code
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
