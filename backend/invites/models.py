from django.conf import settings
from django.db import models


class HomeInvite(models.Model):
    home = models.ForeignKey('devices.Home', on_delete=models.CASCADE, related_name='invites')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_home_invites')
    code_hash = models.CharField(max_length=64, unique=True, db_index=True)
    expires_at = models.DateTimeField(db_index=True)
    used_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='accepted_home_invites', null=True, blank=True)
    used_at = models.DateTimeField(blank=True, null=True, db_index=True)
    revoked_at = models.DateTimeField(blank=True, null=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['home', 'expires_at']),
            models.Index(fields=['home', 'used_at']),
            models.Index(fields=['home', 'revoked_at']),
        ]

    def __str__(self):
        return f'Invite for {self.home} expiring at {self.expires_at}'
