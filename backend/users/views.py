from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import UserSerializer, RegisterSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Register a new user"""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
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
                user = User.objects.get(username=request.data.get('username'))
                response.data['user'] = UserSerializer(user).data
            except User.DoesNotExist:
                pass
        
        return response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """Logout endpoint (simply delete token on frontend)"""
    return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
