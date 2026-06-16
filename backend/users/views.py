import json
from datetime import timedelta

import pyotp
from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import UserMFALoginChallenge, UserMFASettings
from .serializers import (
    MFALoginVerifySerializer,
    MFASetupVerifySerializer,
    RegisterSerializer,
    UserSerializer,
)

MFA_CHALLENGE_LIFETIME = timedelta(minutes=5)


def _request_payload(request):
    data = request.data

    if isinstance(data, dict):
        return data

    if hasattr(data, "dict"):
        return data.dict()

    if isinstance(data, (bytes, bytearray)):
        data = data.decode("utf-8")

    if isinstance(data, str):
        data = data.strip()
        if not data:
            return {}
        try:
            parsed = json.loads(data)
        except json.JSONDecodeError:
            return {}
        return parsed if isinstance(parsed, dict) else {}

    return {}


def _issue_tokens(user):
    refresh = RefreshToken.for_user(user)
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


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    """Register a new user"""
    serializer = RegisterSerializer(data=_request_payload(request))
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "User registered successfully"}, status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user(request):
    """Get current authenticated user info"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    payload = _request_payload(request)
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
        return Response(_issue_tokens(challenge.user), status=status.HTTP_200_OK)

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

    return Response(_issue_tokens(user), status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def mfa_status(request):
    settings = _get_or_create_mfa_settings(request.user)
    return Response({"enabled": settings.enabled}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mfa_setup(request):
    settings = _get_or_create_mfa_settings(request.user)
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


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mfa_verify_setup(request):
    serializer = MFASetupVerifySerializer(data=_request_payload(request))
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


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mfa_disable(request):
    settings = _get_or_create_mfa_settings(request.user)
    settings.enabled = False
    settings.secret = ""
    settings.save(update_fields=["enabled", "secret", "updated_at"])
    UserMFALoginChallenge.objects.filter(user=request.user).delete()
    return Response({"detail": "MFA disabled."}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    """Logout endpoint (blacklist the refresh token)"""
    try:
        payload = _request_payload(request)
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
