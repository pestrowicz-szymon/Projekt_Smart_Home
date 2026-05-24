from django.contrib import admin

from .models import HomeInvite


@admin.register(HomeInvite)
class HomeInviteAdmin(admin.ModelAdmin):
    list_display = ('id', 'home', 'created_by', 'expires_at', 'used_at', 'revoked_at', 'created_at')
    search_fields = ('home__name', 'created_by__username', 'code_hash')
    list_filter = ('used_at', 'revoked_at')
    list_select_related = ('home', 'created_by', 'used_by')
