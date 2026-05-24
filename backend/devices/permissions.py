from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import Device, Home, Room


def user_has_home_access(user, home: Home, write: bool = False) -> bool:
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser or home.owner_id == user.id:
        return True

    membership = home.memberships.filter(user=user).first()
    if membership is None:
        return False

    if write:
        return membership.role in {membership.Role.ADMIN, membership.Role.OWNER} or membership.can_manage_devices
    return True


class CanAccessHome(BasePermission):
    def has_object_permission(self, request, view, obj):
        return user_has_home_access(request.user, obj, write=request.method not in SAFE_METHODS)


class CanAccessDevice(BasePermission):
    def has_object_permission(self, request, view, obj: Device):
        return user_has_home_access(request.user, obj.home, write=request.method not in SAFE_METHODS)


class CanDeleteDevice(BasePermission):
    def has_object_permission(self, request, view, obj: Device):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_superuser or obj.home.owner_id == request.user.id


class CanAccessRoom(BasePermission):
    def has_object_permission(self, request, view, obj: Room):
        return user_has_home_access(request.user, obj.home, write=request.method not in SAFE_METHODS)