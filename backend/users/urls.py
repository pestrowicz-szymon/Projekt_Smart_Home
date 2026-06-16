from django.urls import path
from .views import register, get_user, CustomTokenObtainPairView, logout, update_home_membership

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('me/', get_user, name='get_user'),
    path('memberships/<int:membership_id>/', update_home_membership, name='update_home_membership'),
    path('logout/', logout, name='logout'),
]
