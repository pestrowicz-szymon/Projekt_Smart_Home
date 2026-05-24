from devices.models import Home


def user_can_manage_home_invites(user, home: Home) -> bool:
    if not user or not user.is_authenticated:
        return False
    return user.is_superuser or home.owner_id == user.id
