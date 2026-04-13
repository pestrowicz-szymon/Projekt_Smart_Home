from django.urls import path
from .views import register, get_user, CustomTokenObtainPairView, logout

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('me/', get_user, name='get_user'),
    path('logout/', logout, name='logout'),
]
