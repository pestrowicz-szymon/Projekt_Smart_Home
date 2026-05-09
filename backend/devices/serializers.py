from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Device, DeviceAction, Home, HomeMember, SensorData


class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class HomeMemberSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(source='user', queryset=User.objects.all(), write_only=True)

    class Meta:
        model = HomeMember
        fields = ('id', 'home', 'user', 'user_id', 'role', 'can_manage_devices', 'created_at')
        read_only_fields = ('id', 'home', 'created_at', 'user')

    def validate(self, attrs):
        home = attrs.get('home') or self.context.get('home')
        user = attrs.get('user')
        if home is not None and user is not None and HomeMember.objects.filter(home=home, user=user).exists():
            raise serializers.ValidationError({'user_id': 'This user is already a member of this home.'})
        return attrs


class HomeSerializer(serializers.ModelSerializer):
    owner = UserSummarySerializer(read_only=True)
    members = HomeMemberSerializer(many=True, read_only=True, source='memberships')
    devices_count = serializers.SerializerMethodField()

    class Meta:
        model = Home
        fields = ('id', 'name', 'description', 'owner', 'members', 'devices_count', 'created_at', 'updated_at')
        read_only_fields = ('id', 'owner', 'created_at', 'updated_at', 'devices_count', 'members')

    def get_devices_count(self, obj):
        return obj.devices.count()


class DeviceSerializer(serializers.ModelSerializer):
    home = HomeSerializer(read_only=True)
    home_id = serializers.PrimaryKeyRelatedField(source='home', queryset=Home.objects.all(), write_only=True)

    class Meta:
        model = Device
        fields = (
            'id', 'home', 'home_id', 'name', 'device_type', 'hardware_id', 'status',
            'is_active', 'current_state', 'state_payload', 'certificate_fingerprint',
            'last_seen_at', 'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'home', 'status', 'last_seen_at', 'created_at', 'updated_at')

    def validate(self, attrs):
        request = self.context.get('request')
        home = attrs.get('home') or getattr(self.instance, 'home', None)
        if request and home and not request.user.is_superuser:
            if home.owner_id != request.user.id:
                membership = home.memberships.filter(user=request.user).first()
                if membership is None or not membership.can_manage_devices:
                    raise serializers.ValidationError({'home_id': 'You do not have permission to manage devices in this home.'})
        return attrs


class SensorDataSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source='device.name', read_only=True)

    class Meta:
        model = SensorData
        fields = ('id', 'device', 'device_name', 'metric_name', 'value', 'unit', 'payload', 'source', 'timestamp')
        read_only_fields = ('id', 'timestamp', 'device_name', 'device')


class SensorDataCreateSerializer(serializers.Serializer):
    metric_name = serializers.CharField(max_length=50)
    value = serializers.FloatField(required=False, allow_null=True)
    unit = serializers.CharField(max_length=20, required=False, allow_blank=True)
    payload = serializers.JSONField(required=False, default=dict)


class DeviceActionSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)

    class Meta:
        model = DeviceAction
        fields = ('id', 'device', 'user', 'action_type', 'payload', 'status', 'correlation_id', 'source', 'timestamp')
        read_only_fields = ('id', 'device', 'user', 'status', 'correlation_id', 'source', 'timestamp')


class DeviceCommandCreateSerializer(serializers.Serializer):
    action_type = serializers.CharField(max_length=50)
    payload = serializers.JSONField(required=False, default=dict)