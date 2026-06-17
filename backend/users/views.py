import json
from datetime import timedelta

import pyotp
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from devices.models import HomeMember

from .models import UserMFALoginChallenge, UserMFASettings
from .serializers import (
    CustomTokenRefreshSerializer,
    HomeMembershipSerializer,
    HomeMembershipUpdateSerializer,
    LoginRequestSerializer,
    LoginResponseSerializer,
    MFALoginVerifySerializer,
    MFARequiredResponseSerializer,
    MFASetupResponseSerializer,
    MFASetupVerifySerializer,
    MFAStatusResponseSerializer,
    RegisterSerializer,
    UserSerializer,
)

MFA_CHALLENGE_LIFETIME = timedelta(minutes=5)


def user_can_manage_home_members(user, membership):
    home = membership.home
    if user.is_superuser or home.owner_id == user.id:
        return True

    # Check if the user is an admin in this home
    user_membership = home.memberships.filter(user=user).first()
    return user_membership and user_membership.role == HomeMember.Role.ADMIN


def _issue_tokens(user, mfa_verified=False):
    refresh = RefreshToken.for_user(user)
    # Add custom claim to both tokens to support persistence across refreshes
    refresh["mfa_verified"] = mfa_verified
    refresh.access_token["mfa_verified"] = mfa_verified

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
        "user": UserSerializer(user).data,
    }


def _get_or_create_mfa_settings(user):
    settings, _ = UserMFASettings.objects.get_or_create(user=user)
    return settings


def _verify_totp(secret: str, code: str) -> bool:
    if not secret:
        return False
    totp = pyotp.TOTP(secret)
    return bool(totp.verify(code, valid_window=1))


@extend_schema(
    tags=["auth"],
    summary="Register a new user",
    request=RegisterSerializer,
    responses={
        201: inline_serializer("RegisterSuccess", {"message": serializers.CharField()}),
        400: OpenApiTypes.OBJECT,
    },
)
@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    """Register a new user"""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "User registered successfully"}, status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["auth"],
    summary="Get current user info",
    responses={200: UserSerializer},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user(request):
    """Get current authenticated user info"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@extend_schema(
    tags=["auth"],
    summary="Login",
    description="Authenticates a user and returns JWT tokens. Supports MFA if enabled.",
    request=LoginRequestSerializer,
    responses={
        200: LoginResponseSerializer,
        202: MFARequiredResponseSerializer,
        401: OpenApiTypes.OBJECT,
    },
)
@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    payload = request.data
    mfa_token = payload.get("mfa_token")
    if mfa_token:
        serializer = MFALoginVerifySerializer(data=payload)
        serializer.is_valid(raise_exception=True)

        try:
            challenge = UserMFALoginChallenge.objects.select_related("user").get(
                token=serializer.validated_data["mfa_token"]
            )
        except UserMFALoginChallenge.DoesNotExist:
            return Response(
                {"detail": "Invalid MFA challenge."}, status=status.HTTP_400_BAD_REQUEST
            )

        if challenge.consumed_at is not None or challenge.expires_at <= timezone.now():
            return Response(
                {"detail": "MFA challenge expired."}, status=status.HTTP_400_BAD_REQUEST
            )

        settings = _get_or_create_mfa_settings(challenge.user)
        if not settings.enabled or not _verify_totp(
            settings.secret, serializer.validated_data["mfa_code"]
        ):
            return Response(
                {"detail": "Invalid MFA code."}, status=status.HTTP_400_BAD_REQUEST
            )

        challenge.consumed_at = timezone.now()
        challenge.save(update_fields=["consumed_at"])
        # MFA passed, issue token with mfa_verified=True
        return Response(
            _issue_tokens(challenge.user, mfa_verified=True), status=status.HTTP_200_OK
        )

    username = payload.get("username")
    password = payload.get("password")
    user = authenticate(request, username=username, password=password)
    if user is None:
        return Response(
            {"detail": "No active account found with the given credentials."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    settings = _get_or_create_mfa_settings(user)
    if settings.enabled and settings.secret:
        challenge = UserMFALoginChallenge.objects.create(
            user=user,
            expires_at=timezone.now() + MFA_CHALLENGE_LIFETIME,
        )
        return Response(
            {
                "mfa_required": True,
                "mfa_token": str(challenge.token),
                "expires_at": challenge.expires_at,
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )

    # MFA disabled, issue token with mfa_verified=True (trusted since MFA is off)
    return Response(_issue_tokens(user, mfa_verified=True), status=status.HTTP_200_OK)


@extend_schema(
    tags=["mfa"],
    summary="Get MFA status",
    responses={200: MFAStatusResponseSerializer},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def mfa_status(request):
    settings = _get_or_create_mfa_settings(request.user)
    return Response({"enabled": settings.enabled}, status=status.HTTP_200_OK)


@extend_schema(
    tags=["mfa"],
    summary="Setup MFA",
    request=None,
    responses={200: MFASetupResponseSerializer},
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mfa_setup(request):
    settings = _get_or_create_mfa_settings(request.user)
    if settings.enabled:
        return Response(
            {"detail": "MFA is already enabled for this account."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not settings.secret:
        settings.secret = pyotp.random_base32()
        settings.enabled = False
        settings.save(update_fields=["secret", "enabled", "updated_at"])

    totp = pyotp.TOTP(settings.secret)
    return Response(
        {
            "mfa_enabled": settings.enabled,
            "secret": settings.secret,
            "otpauth_uri": totp.provisioning_uri(
                name=request.user.username, issuer_name="Smart Home"
            ),
        },
        status=status.HTTP_200_OK,
    )


@extend_schema(
    tags=["mfa"],
    summary="Verify MFA setup",
    request=MFASetupVerifySerializer,
    responses={200: MFAStatusResponseSerializer, 400: OpenApiTypes.OBJECT},
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mfa_verify_setup(request):
    serializer = MFASetupVerifySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    settings = _get_or_create_mfa_settings(request.user)
    if not settings.secret:
        return Response(
            {"detail": "MFA setup has not been initialized."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not _verify_totp(settings.secret, serializer.validated_data["code"]):
        return Response(
            {"detail": "Invalid MFA code."}, status=status.HTTP_400_BAD_REQUEST
        )

    settings.enabled = True
    settings.save(update_fields=["enabled", "updated_at"])
    return Response({"enabled": True}, status=status.HTTP_200_OK)


@extend_schema(
    tags=["mfa"],
    summary="Disable MFA",
    request=None,
    responses={
        200: inline_serializer("MFADisableSuccess", {"detail": serializers.CharField()})
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mfa_disable(request):
    settings = _get_or_create_mfa_settings(request.user)
    settings.enabled = False
    settings.secret = ""
    settings.save(update_fields=["enabled", "secret", "updated_at"])
    UserMFALoginChallenge.objects.filter(user=request.user).delete()
    return Response({"detail": "MFA disabled."}, status=status.HTTP_200_OK)


@extend_schema(
    tags=["auth"],
    summary="Logout",
    request=inline_serializer("LogoutRequest", {"refresh": serializers.CharField()}),
    responses={
        200: inline_serializer("LogoutSuccess", {"message": serializers.CharField()}),
        400: OpenApiTypes.OBJECT,
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    """Logout endpoint (blacklist the refresh token)"""
    try:
        payload = request.data
        refresh_token = payload.get("refresh")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        return Response(
            {"detail": "Refresh token required"}, status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["auth"],
    summary="Update home membership",
    request=inline_serializer(
        "HomeMembershipUpdate", {"can_manage_devices": serializers.BooleanField()}
    ),
    responses={200: HomeMembershipSerializer},
)
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_home_membership(request, membership_id: int):
    """Update a home membership, e.g. enable device management."""
    membership = get_object_or_404(
        HomeMember.objects.select_related("home"), pk=membership_id
    )
    if not user_can_manage_home_members(request.user, membership):
        return Response(
            {"detail": "Only home owners or admins can update membership permissions."},
            status=status.HTTP_403_FORBIDDEN,
        )
    serializer = HomeMembershipUpdateSerializer(
        membership, data=request.data, partial=True
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(HomeMembershipSerializer(membership).data)


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer
