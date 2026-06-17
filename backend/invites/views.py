from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from devices.models import Home

from .permissions import user_can_manage_home_invites
from .serializers import (
    HomeInviteCreateSerializer,
    HomeInviteRedeemSerializer,
    HomeInviteSerializer,
    HomeMemberInviteSerializer,
)
from .services import create_home_invite, redeem_home_invite

HOME_INVITE_CREATE_RESPONSE_EXAMPLE = OpenApiExample(
    "Create home invite",
    value={
        "id": 5,
        "home": 1,
        "created_by": {
            "id": 7,
            "first_name": "Anna",
            "last_name": "Nowak",
        },
        "code": "d4f9e1f0d7d64ab8c2fcbf1c0f1a90bb",
        "expires_at": "2026-05-24T10:30:00Z",
        "used_by": None,
        "used_at": None,
        "revoked_at": None,
        "status": "active",
        "created_at": "2026-05-24T10:00:00Z",
        "updated_at": "2026-05-24T10:00:00Z",
    },
    response_only=True,
)

HOME_INVITE_LIST_EXAMPLE = OpenApiExample(
    "List home invites",
    value=[
        {
            "id": 5,
            "home": 1,
            "created_by": {
                "id": 7,
                "first_name": "Anna",
                "last_name": "Nowak",
            },
            "expires_at": "2026-05-24T10:30:00Z",
            "used_by": None,
            "used_at": None,
            "revoked_at": None,
            "status": "active",
            "created_at": "2026-05-24T10:00:00Z",
            "updated_at": "2026-05-24T10:00:00Z",
        },
    ],
    response_only=True,
)

HOME_INVITE_REDEEM_EXAMPLE = OpenApiExample(
    "Redeem invite",
    value={"code": "d4f9e1f0d7d64ab8c2fcbf1c0f1a90bb"},
    request_only=True,
)

HOME_INVITE_REDEEM_RESPONSE_EXAMPLE = OpenApiExample(
    "Redeem invite response",
    value={
        "id": 21,
        "home": 1,
        "user": {
            "id": 12,
            "first_name": "Jan",
            "last_name": "Kowalski",
        },
        "role": "member",
        "can_manage_devices": False,
        "created_at": "2026-05-24T10:00:00Z",
    },
    response_only=True,
)


@extend_schema(
    tags=["invites"],
    summary="List or create home invites",
    request=HomeInviteCreateSerializer,
    examples=[HOME_INVITE_CREATE_RESPONSE_EXAMPLE, HOME_INVITE_LIST_EXAMPLE],
    responses={200: HomeInviteSerializer(many=True), 201: HomeInviteSerializer},
)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def home_invites(request, home_id):
    home = get_object_or_404(
        Home.objects.select_related("owner").prefetch_related(
            "memberships__user", "devices", "rooms"
        ),
        pk=home_id,
    )
    if not user_can_manage_home_invites(request.user, home):
        return Response(
            {"detail": "Only the home owner can manage invitations."},
            status=status.HTTP_403_FORBIDDEN,
        )

    if request.method == "GET":
        serializer = HomeInviteSerializer(
            home.invites.select_related("created_by", "used_by").all(), many=True
        )
        return Response(serializer.data)

    serializer = HomeInviteCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    invite, raw_code = create_home_invite(home=home, created_by=request.user)
    serializer = HomeInviteSerializer(invite, context={"code": raw_code})
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=["invites"],
    summary="Redeem a home invitation code",
    description=(
        "Use this endpoint after logging in. Send a POST request with a JSON body like "
        '`{"code": "<invite_code>"}`. The code is one-time use; if it is valid, the current '
        "user is added to the target home and the response contains the created HomeMember record."
    ),
    request=HomeInviteRedeemSerializer,
    examples=[HOME_INVITE_REDEEM_EXAMPLE, HOME_INVITE_REDEEM_RESPONSE_EXAMPLE],
    responses={
        201: HomeMemberInviteSerializer,
        400: OpenApiResponse(
            description="The code is missing, invalid, expired, or already used."
        ),
        401: OpenApiResponse(description="Authentication required."),
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def redeem_invite(request):
    serializer = HomeInviteRedeemSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    membership = redeem_home_invite(
        code_hash=serializer.validated_data["code"], user=request.user
    )
    return Response(
        HomeMemberInviteSerializer(membership).data, status=status.HTTP_201_CREATED
    )
