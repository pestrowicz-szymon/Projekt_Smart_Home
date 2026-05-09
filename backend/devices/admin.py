from django.contrib import admin

from .models import Device, DeviceAction, Home, HomeMember, SensorData


@admin.register(Home)
class HomeAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'owner', 'created_at')
	search_fields = ('name', 'owner__username')
	list_select_related = ('owner',)


@admin.register(HomeMember)
class HomeMemberAdmin(admin.ModelAdmin):
	list_display = ('id', 'home', 'user', 'role', 'can_manage_devices', 'created_at')
	search_fields = ('home__name', 'user__username')
	list_select_related = ('home', 'user')


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'device_type', 'home', 'status', 'is_active', 'last_seen_at')
	search_fields = ('name', 'hardware_id', 'home__name')
	list_filter = ('device_type', 'status', 'is_active')
	list_select_related = ('home',)


@admin.register(SensorData)
class SensorDataAdmin(admin.ModelAdmin):
	list_display = ('id', 'device', 'metric_name', 'value', 'unit', 'timestamp')
	search_fields = ('device__name', 'metric_name')
	list_select_related = ('device',)


@admin.register(DeviceAction)
class DeviceActionAdmin(admin.ModelAdmin):
	list_display = ('id', 'device', 'action_type', 'status', 'user', 'source', 'timestamp')
	search_fields = ('device__name', 'action_type', 'correlation_id', 'user__username')
	list_filter = ('status', 'source', 'action_type')
	list_select_related = ('device', 'user')