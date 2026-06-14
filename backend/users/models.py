import uuid

from django.contrib.auth.models import User
from django.db import models


class UserMFASettings(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mfa_settings')
	secret = models.CharField(max_length=64, blank=True, default='')
	enabled = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f'MFA settings for {self.user.username}'


class UserMFALoginChallenge(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mfa_login_challenges')
	token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
	expires_at = models.DateTimeField()
	consumed_at = models.DateTimeField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f'MFA login challenge for {self.user.username}'
