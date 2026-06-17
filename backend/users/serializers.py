from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from devices.models import HomeMember

from .models import UserMFASettings


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        # Copy mfa_verified claim from the old refresh token to the new access token
        refresh = RefreshToken(attrs["refresh"])
        mfa_verified = refresh.get("mfa_verified", False)

        # Data contains 'access' (and maybe 'refresh' if rotation is enabled)
        # We need to re-encode the access token with the claim
        access = RefreshToken(attrs["refresh"]).access_token
        access["mfa_verified"] = mfa_verified
        data["access"] = str(access)

        # If refresh token rotation is on, also preserve it in the new refresh token
        if "refresh" in data:
            new_refresh = RefreshToken(data["refresh"])
            new_refresh["mfa_verified"] = mfa_verified
            data["refresh"] = str(new_refresh)

        return data


class HomeMembershipSerializer(serializers.ModelSerializer):
    home = serializers.SerializerMethodField()

    class Meta:
        model = HomeMember
        fields = ("id", "home", "role", "can_manage_devices", "created_at")
        read_only_fields = fields

    def get_home(self, obj) -> dict:
        return {
            "id": obj.home_id,
            "name": obj.home.name,
            "description": obj.home.description,
        }


class HomeMembershipUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeMember
        fields = ("can_manage_devices",)


class UserSerializer(serializers.ModelSerializer):
    home_memberships = serializers.SerializerMethodField()
    mfa_enabled = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "home_memberships",
            "mfa_enabled",
        )

    def get_home_memberships(self, obj) -> list[dict]:
        memberships = (
            obj.home_memberships.select_related("home").all().order_by("created_at")
        )
        return HomeMembershipSerializer(memberships, many=True).data

    def get_mfa_enabled(self, obj) -> bool:
        try:
            return bool(obj.mfa_settings.enabled)
        except UserMFASettings.DoesNotExist:
            return False


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
            "password2",
            "first_name",
            "last_name",
        )

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return data

    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create_user(**validated_data)
        return user


class MFALoginVerifySerializer(serializers.Serializer):
    mfa_token = serializers.UUIDField()
    mfa_code = serializers.CharField(max_length=8)


class MFASetupVerifySerializer(serializers.Serializer):
    code = serializers.CharField(max_length=8)


class LoginRequestSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    password = serializers.CharField(required=False, write_only=True)
    mfa_token = serializers.UUIDField(required=False)
    mfa_code = serializers.CharField(required=False, max_length=8)


class LoginResponseSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()
    user = UserSerializer()


class MFARequiredResponseSerializer(serializers.Serializer):
    mfa_required = serializers.BooleanField(default=True)
    mfa_token = serializers.UUIDField()
    expires_at = serializers.DateTimeField()
    user = UserSerializer()


class MFASetupResponseSerializer(serializers.Serializer):
    mfa_enabled = serializers.BooleanField()
    secret = serializers.CharField()
    otpauth_uri = serializers.CharField()


class MFAStatusResponseSerializer(serializers.Serializer):
    enabled = serializers.BooleanField()


class TokenRefreshResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField(required=False)
