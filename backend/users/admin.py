from django.contrib import admin

from .models import UserMFALoginChallenge, UserMFASettings


@admin.register(UserMFASettings)
class UserMFASettingsAdmin(admin.ModelAdmin):
	list_display = ('user', 'enabled', 'created_at', 'updated_at')
	list_filter = ('enabled',)
	search_fields = ('user__username',)


@admin.register(UserMFALoginChallenge)
class UserMFALoginChallengeAdmin(admin.ModelAdmin):
	list_display = ('user', 'token', 'expires_at', 'consumed_at', 'created_at')
	list_filter = ('consumed_at',)
	search_fields = ('user__username', 'token')
