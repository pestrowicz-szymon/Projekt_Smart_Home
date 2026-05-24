from django.urls import path

from .views import home_invites, redeem_invite

urlpatterns = [
    path('homes/<int:home_id>/invites/', home_invites, name='home_invites'),
    path('invites/redeem/', redeem_invite, name='invite_redeem'),
]
