from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from devices.models import HomeMember

from .serializers import HomeMembershipSerializer, HomeMembershipUpdateSerializer, RegisterSerializer, UserSerializer


def user_can_manage_home_members(user, membership: HomeMember) -> bool:
    if not user or not user.is_authenticated:
        return False
    home = membership.home
    if user.is_superuser or home.owner_id == user.id:
        return True
    owner_membership = home.memberships.filter(user=user).first()
    if owner_membership is None:
        return False
    return owner_membership.role in {HomeMember.Role.ADMIN, HomeMember.Role.OWNER}


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


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user(request):
    """Get current authenticated user info"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Login endpoint - zwraca tokeny + dane użytkownika"""

    def post(self, request, *args, **kwargs):
        # Standardowa logika logowania (walidacja + generowanie tokenów)
        response = super().post(request, *args, **kwargs)

        # Jeśli logowanie się powiodło, dodaj dane użytkownika
        if response.status_code == 200:
            try:
                user = User.objects.get(username=request.data.get("username"))
                response.data["user"] = UserSerializer(user).data
            except User.DoesNotExist:
                pass

        return response


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    """Logout endpoint (simply delete token on frontend)"""
    return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_home_membership(request, membership_id: int):
    """Update a home membership, e.g. enable device management."""
    membership = get_object_or_404(HomeMember.objects.select_related('home'), pk=membership_id)
    if not user_can_manage_home_members(request.user, membership):
        return Response(
            {'detail': 'Only home owners or admins can update membership permissions.'},
            status=status.HTTP_403_FORBIDDEN,
        )
    serializer = HomeMembershipUpdateSerializer(membership, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(HomeMembershipSerializer(membership).data)
