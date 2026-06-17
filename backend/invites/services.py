import hashlib
import secrets
from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from devices.models import Home, HomeMember

from .models import HomeInvite

INVITE_CODE_BYTES = 16
INVITE_TTL_MINUTES = 30


class InviteError(serializers.ValidationError):
    pass


def hash_invite_code(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def generate_invite_code() -> str:
    return secrets.token_hex(INVITE_CODE_BYTES)


def create_home_invite(
    *, home: Home, created_by, expires_in_minutes: int = INVITE_TTL_MINUTES
) -> tuple[HomeInvite, str]:
    raw_code = generate_invite_code()
    invite = HomeInvite.objects.create(
        home=home,
        created_by=created_by,
        code_hash=hash_invite_code(raw_code),
        expires_at=timezone.now() + timedelta(minutes=expires_in_minutes),
    )
    return invite, raw_code


@transaction.atomic
def redeem_home_invite(*, raw_code: str, user) -> HomeMember:
    code_hash = raw_code
    invite = (
        HomeInvite.objects.select_for_update()
        .select_related("home")
        .filter(code_hash=code_hash)
        .first()
    )
    if invite is None:
        raise InviteError({"code": "Invalid invitation code."})

    now = timezone.now()
    if invite.revoked_at is not None:
        raise InviteError({"code": "This invitation code has been revoked."})
    if invite.used_at is not None:
        raise InviteError({"code": "This invitation code has already been used."})
    if invite.expires_at <= now:
        raise InviteError({"code": "This invitation code has expired."})
    if HomeMember.objects.filter(home=invite.home, user=user).exists():
        raise InviteError({"code": "You are already a member of this home."})

    membership = HomeMember.objects.create(home=invite.home, user=user)
    invite.used_by = user
    invite.used_at = now
    invite.save(update_fields=["used_by", "used_at", "updated_at"])
    return membership
