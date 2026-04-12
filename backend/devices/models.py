from django.db import models
from django.contrib.auth.models import User

class Home(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Device(models.Model):
    DEVICE_TYPES = [
        ('thermometer', 'Termometr'),
        ('lock', 'Zamek elektroniczny'),
        ('light', 'Oświetlenie'),
        ('smoke_detector', 'Czujnik dymu'),
    ]

    home = models.ForeignKey(Home, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPES)
    hardware_id = models.CharField(max_length=100, unique=True)
    current_state = models.FloatField(default=0)

    def __str__(self):
        return f"{self.name} ({self.device_type})"
    
class SensorData(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    value = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.device.name} - {self.value} at {self.timestamp}"
    
class DeviceAction(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action_type = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device.name} - {self.action_type} by {self.user} at {self.timestamp}"