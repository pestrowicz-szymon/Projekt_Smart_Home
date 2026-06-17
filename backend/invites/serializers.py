from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import serializers

from devices.models import HomeMember

from .models import HomeInvite


class PublicUserInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name")
        ref_name = "PublicUserInvite"


class HomeInviteSerializer(serializers.ModelSerializer):
    created_by = PublicUserInviteSerializer(read_only=True)
    used_by = PublicUserInviteSerializer(read_only=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = HomeInvite
        fields = (
            "id",
            "home",
            "created_by",
            "expires_at",
            "used_by",
            "used_at",
            "revoked_at",
            "code_hash",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "home",
            "created_by",
            "expires_at",
            "used_by",
            "used_at",
            "revoked_at",
            "code_hash",
            "status",
            "created_at",
            "updated_at",
        )

    def get_status(self, obj) -> str:
        if obj.revoked_at is not None:
            return "revoked"
        if obj.used_at is not None:
            return "used"
        return "active" if obj.expires_at > timezone.now() else "expired"

    def get_code(self, obj):
        return self.context.get("code")


class HomeInviteCreateSerializer(serializers.Serializer):
    pass


class HomeInviteRedeemSerializer(serializers.Serializer):
    code = serializers.CharField(
        max_length=64,
        trim_whitespace=True,
        help_text="Invitation code from the invite link or QR code. Send it in POST /api/invites/invites/redeem/.",
    )


class HomeMemberInviteSerializer(serializers.ModelSerializer):
    user = PublicUserInviteSerializer(read_only=True)

    class Meta:
        model = HomeMember
        fields = ("id", "home", "user", "role", "can_manage_devices", "created_at")
        read_only_fields = ("id", "home", "user", "created_at")
        ref_name = "HomeMemberInvite"
