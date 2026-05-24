from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory, force_authenticate

from devices.models import Home

from .services import create_home_invite, hash_invite_code, redeem_home_invite
from .views import home_invites, redeem_invite


class HomeInviteTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='password123')
        self.home = Home.objects.create(name='Main Home', description='Primary home', owner=self.owner)
        self.joiner = User.objects.create_user(username='joiner', password='password123')

    def test_create_home_invite_stores_hash_only(self):
        invite, raw_code = create_home_invite(home=self.home, created_by=self.owner)

        self.assertIsInstance(raw_code, str)
        self.assertNotEqual(invite.code_hash, raw_code)
        self.assertEqual(invite.code_hash, hash_invite_code(raw_code))
        self.assertTrue(raw_code)

    def test_redeem_home_invite_is_one_time_only(self):
        invite, raw_code = create_home_invite(home=self.home, created_by=self.owner)

        membership = redeem_home_invite(code=raw_code, user=self.joiner)

        self.assertEqual(membership.home_id, self.home.id)
        self.assertEqual(membership.user_id, self.joiner.id)

        invite.refresh_from_db()
        self.assertIsNotNone(invite.used_at)
        self.assertEqual(invite.used_by_id, self.joiner.id)

        with self.assertRaises(ValidationError):
            redeem_home_invite(code=raw_code, user=User.objects.create_user(username='late', password='password123'))

    def test_expired_home_invite_is_rejected(self):
        invite, raw_code = create_home_invite(home=self.home, created_by=self.owner)
        invite.expires_at = timezone.now() - timedelta(minutes=1)
        invite.save(update_fields=['expires_at'])

        with self.assertRaises(ValidationError):
            redeem_home_invite(code=raw_code, user=self.joiner)

    def test_home_invite_views_require_owner_for_generation_and_login_for_redeem(self):
        factory = APIRequestFactory()
        request = factory.post('/api/invites/homes/1/invites/', {})
        force_authenticate(request, user=self.owner)

        response = home_invites(request, home_id=self.home.id)
        self.assertEqual(response.status_code, 201)
        self.assertIn('code', response.data)

        redeem_request = factory.post('/api/invites/redeem/', {'code': response.data['code']}, format='json')
        force_authenticate(redeem_request, user=self.joiner)

        redeem_response = redeem_invite(redeem_request)
        self.assertEqual(redeem_response.status_code, 201)
        self.assertEqual(redeem_response.data['home'], self.home.id)
