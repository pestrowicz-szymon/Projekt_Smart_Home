from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from devices.models import Home, HomeMember

from .views import get_user


class GetUserTests(TestCase):
	def test_get_user_includes_home_memberships(self):
		user = User.objects.create_user(username='john', email='john@example.com', password='password123')
		home = Home.objects.create(name='Main Home', description='Primary home', owner=user)
		HomeMember.objects.create(home=home, user=user, role=HomeMember.Role.ADMIN, can_manage_devices=True)

		request = APIRequestFactory().get('/api/users/me/')
		force_authenticate(request, user=user)

		response = get_user(request)

		self.assertEqual(response.status_code, 200)
		self.assertIn('home_memberships', response.data)
		self.assertEqual(len(response.data['home_memberships']), 1)
		membership = response.data['home_memberships'][0]
		self.assertEqual(membership['home']['id'], home.id)
		self.assertEqual(membership['home']['name'], 'Main Home')
		self.assertEqual(membership['role'], HomeMember.Role.ADMIN)
		self.assertTrue(membership['can_manage_devices'])
