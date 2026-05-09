from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DeviceActionViewSet, DeviceViewSet, HomeViewSet, SensorDataViewSet


router = DefaultRouter()
router.register(r'homes', HomeViewSet, basename='home')
router.register(r'devices', DeviceViewSet, basename='device')
router.register(r'actions', DeviceActionViewSet, basename='device-action')
router.register(r'readings', SensorDataViewSet, basename='sensor-reading')

urlpatterns = [
    path('', include(router.urls)),
]