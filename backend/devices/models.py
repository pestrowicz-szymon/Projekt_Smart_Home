from django.conf import settings
from django.db import models


class Home(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_homes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class HomeMember(models.Model):
    class Role(models.TextChoices):
        OWNER = 'owner', 'Owner'
        ADMIN = 'admin', 'Admin'
        MEMBER = 'member', 'Member'
        VIEWER = 'viewer', 'Viewer'

    home = models.ForeignKey(Home, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='home_memberships')
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBER)
    can_manage_devices = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['home', 'user'], name='unique_home_member'),
        ]

    def __str__(self):
        return f'{self.user} in {self.home} ({self.role})'


class Room(models.Model):
    home = models.ForeignKey(Home, on_delete=models.CASCADE, related_name='rooms')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['home', 'name'], name='unique_room_per_home'),
        ]
        indexes = [
            models.Index(fields=['home', 'name']),
        ]

    def __str__(self):
        return f'{self.name} ({self.home})'


class Device(models.Model):
    class DeviceType(models.TextChoices):
        THERMOMETER = 'thermometer', 'Termometr'
        LOCK = 'lock', 'Zamek elektroniczny'
        LIGHT = 'light', 'Oświetlenie'
        SMOKE_DETECTOR = 'smoke_detector', 'Czujnik dymu'
        GENERIC_SENSOR = 'generic_sensor', 'Czujnik ogólny'
        ACTUATOR = 'actuator', 'Aktuator'

    class Status(models.TextChoices):
        UNKNOWN = 'unknown', 'Unknown'
        ONLINE = 'online', 'Online'
        OFFLINE = 'offline', 'Offline'

    home = models.ForeignKey(Home, on_delete=models.CASCADE, related_name='devices')
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, related_name='devices', blank=True, null=True)
    name = models.CharField(max_length=100)
    device_type = models.CharField(max_length=20, choices=DeviceType.choices)
    hardware_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UNKNOWN)
    is_active = models.BooleanField(default=True)
    current_state = models.FloatField(default=0)
    state_payload = models.JSONField(default=dict, blank=True)
    certificate_fingerprint = models.CharField(max_length=128, blank=True, null=True, unique=True)
    last_seen_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['home', 'device_type']),
            models.Index(fields=['home', 'room']),
            models.Index(fields=['hardware_id']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.name} ({self.device_type})"


class SensorData(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='readings')
    metric_name = models.CharField(max_length=50, default='value')
    value = models.FloatField(blank=True, null=True)
    unit = models.CharField(max_length=20, blank=True, default='')
    payload = models.JSONField(default=dict, blank=True)
    source = models.CharField(max_length=30, default='mq')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['device', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.device.name} - {self.metric_name} at {self.timestamp}"


class DeviceAction(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SENT = 'sent', 'Sent'
        ACKED = 'acked', 'Acked'
        FAILED = 'failed', 'Failed'
        CANCELLED = 'cancelled', 'Cancelled'

    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='actions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='device_actions')
    action_type = models.CharField(max_length=50)
    payload = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    correlation_id = models.CharField(max_length=64, blank=True, default='')
    source = models.CharField(max_length=30, default='api')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['device', '-timestamp']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        actor = self.user if self.user else 'system'
        return f"{self.device.name} - {self.action_type} by {actor} at {self.timestamp}"