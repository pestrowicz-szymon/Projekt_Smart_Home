from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    DeviceActionViewSet,
    DeviceEventStreamView,
    DeviceViewSet,
    HomeViewSet,
    RoomViewSet,
    SensorDataViewSet,
)

router = DefaultRouter()
router.register(r"homes", HomeViewSet, basename="home")
router.register(r"rooms", RoomViewSet, basename="room")
router.register(r"devices", DeviceViewSet, basename="device")
router.register(r"actions", DeviceActionViewSet, basename="device-action")
router.register(r"readings", SensorDataViewSet, basename="sensor-reading")

urlpatterns = [
    path("events/", DeviceEventStreamView.as_view(), name="device-events"),
    path("", include(router.urls)),
]
