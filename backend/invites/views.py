from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view

from devices.models import Home

from .permissions import user_can_manage_home_invites
from .serializers import HomeInviteCreateSerializer, HomeInviteRedeemSerializer, HomeInviteSerializer, HomeMemberSerializer
from .services import create_home_invite, redeem_home_invite

HOME_INVITE_CREATE_RESPONSE_EXAMPLE = OpenApiExample(
    'Create home invite',
    value={
        'id': 5,
        'home': 1,
        'created_by': {
            'id': 7,
            'first_name': 'Anna',
            'last_name': 'Nowak',
        },
        'code': 'd4f9e1f0d7d64ab8c2fcbf1c0f1a90bb',
        'expires_at': '2026-05-24T10:30:00Z',
        'used_by': None,
        'used_at': None,
        'revoked_at': None,
        'status': 'active',
        'created_at': '2026-05-24T10:00:00Z',
        'updated_at': '2026-05-24T10:00:00Z',
    },
    response_only=True,
)

HOME_INVITE_LIST_EXAMPLE = OpenApiExample(
    'List home invites',
    value=[
        {
            'id': 5,
            'home': 1,
            'created_by': {
                'id': 7,
                'first_name': 'Anna',
                'last_name': 'Nowak',
            },
            'expires_at': '2026-05-24T10:30:00Z',
            'used_by': None,
            'used_at': None,
            'revoked_at': None,
            'status': 'active',
            'created_at': '2026-05-24T10:00:00Z',
            'updated_at': '2026-05-24T10:00:00Z',
        },
    ],
    response_only=True,
)

HOME_INVITE_REDEEM_EXAMPLE = OpenApiExample(
    'Redeem invite',
    value={'code': 'd4f9e1f0d7d64ab8c2fcbf1c0f1a90bb'},
    request_only=True,
)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@extend_schema(
    tags=['invites'],
    summary='List or create home invites',
    request=HomeInviteCreateSerializer,
    examples=[HOME_INVITE_CREATE_RESPONSE_EXAMPLE, HOME_INVITE_LIST_EXAMPLE],
    responses={200: HomeInviteSerializer(many=True), 201: HomeInviteSerializer},
)
def home_invites(request, home_id):
    home = get_object_or_404(Home.objects.select_related('owner').prefetch_related('memberships__user', 'devices', 'rooms'), pk=home_id)
    if not user_can_manage_home_invites(request.user, home):
        return Response({'detail': 'Only the home owner can manage invitations.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = HomeInviteSerializer(home.invites.select_related('created_by', 'used_by').all(), many=True)
        return Response(serializer.data)

    serializer = HomeInviteCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    invite, raw_code = create_home_invite(home=home, created_by=request.user)
    response_data = HomeInviteSerializer(invite).data
    response_data['code'] = raw_code
    return Response(response_data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@extend_schema(
    tags=['invites'],
    summary='Redeem a home invitation code',
    request=HomeInviteRedeemSerializer,
    examples=[HOME_INVITE_REDEEM_EXAMPLE],
    responses={201: HomeMemberSerializer},
)
def redeem_invite(request):
    serializer = HomeInviteRedeemSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    membership = redeem_home_invite(code=serializer.validated_data['code'], user=request.user)
    return Response(HomeMemberSerializer(membership).data, status=status.HTTP_201_CREATED)
