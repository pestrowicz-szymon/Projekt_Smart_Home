from django.contrib import admin
from .models import Home, Device, SensorData, DeviceAction

# Register your models here.
admin.site.register(Home)
admin.site.register(Device)
admin.site.register(SensorData)
admin.site.register(DeviceAction)