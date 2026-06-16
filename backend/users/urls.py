from django.urls import path

from .views import (
    get_user,
    login,
    logout,
    mfa_disable,
    mfa_setup,
    mfa_status,
    mfa_verify_setup,
    register,
)

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('me/', get_user, name='get_user'),
    path('memberships/<int:membership_id>/', update_home_membership, name='update_home_membership'),
    path('logout/', logout, name='logout'),
    path('mfa/status/', mfa_status, name='mfa_status'),
    path('mfa/setup/', mfa_setup, name='mfa_setup'),
    path('mfa/verify/', mfa_verify_setup, name='mfa_verify'),
    path('mfa/disable/', mfa_disable, name='mfa_disable'),
]
