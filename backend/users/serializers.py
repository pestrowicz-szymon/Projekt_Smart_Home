from django.contrib.auth.models import User
from rest_framework import serializers

from devices.models import HomeMember


class HomeMembershipSerializer(serializers.ModelSerializer):
    home = serializers.SerializerMethodField()

    class Meta:
        model = HomeMember
        fields = ('id', 'home', 'role', 'can_manage_devices', 'created_at')
        read_only_fields = fields

    def get_home(self, obj):
        return {
            'id': obj.home_id,
            'name': obj.home.name,
            'description': obj.home.description,
        }


class HomeMembershipUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeMember
        fields = ('can_manage_devices',)


class UserSerializer(serializers.ModelSerializer):
    home_memberships = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'home_memberships')

    def get_home_memberships(self, obj):
        memberships = obj.home_memberships.select_related('home').all().order_by('created_at')
        return HomeMembershipSerializer(memberships, many=True).data


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'first_name', 'last_name')

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user
