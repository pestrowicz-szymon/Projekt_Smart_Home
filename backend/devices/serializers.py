from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.permissions import SAFE_METHODS

from .models import Device, DeviceAction, Home, HomeMember, Room, SensorData
from .permissions import user_has_home_access


class PublicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name")


class HomeMemberSerializer(serializers.ModelSerializer):
    user = PublicUserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        source="user", queryset=User.objects.all(), write_only=True
    )

    class Meta:
        model = HomeMember
        fields = (
            "id",
            "home",
            "user",
            "user_id",
            "role",
            "can_manage_devices",
            "created_at",
        )
        read_only_fields = ("id", "home", "created_at", "user")

    def validate(self, attrs):
        home = attrs.get("home") or self.context.get("home")
        user = attrs.get("user")
        if (
            home is not None
            and user is not None
            and HomeMember.objects.filter(home=home, user=user).exists()
        ):
            raise serializers.ValidationError(
                {"user_id": "This user is already a member of this home."}
            )
        return attrs


class HomeSerializer(serializers.ModelSerializer):
    owner = PublicUserSerializer(read_only=True)
    members = HomeMemberSerializer(many=True, read_only=True, source="memberships")
    rooms = serializers.SerializerMethodField()
    devices_count = serializers.SerializerMethodField()

    class Meta:
        model = Home
        fields = (
            "id",
            "name",
            "description",
            "owner",
            "members",
            "rooms",
            "devices_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "owner",
            "created_at",
            "updated_at",
            "devices_count",
            "members",
            "rooms",
        )

    def get_rooms(self, obj):
        return RoomSerializer(obj.rooms.all(), many=True).data

    def get_devices_count(self, obj):
        return obj.devices.count()


class RoomSerializer(serializers.ModelSerializer):
    home = serializers.PrimaryKeyRelatedField(read_only=True)
    home_id = serializers.PrimaryKeyRelatedField(
        source="home", queryset=Home.objects.all(), write_only=True
    )

    class Meta:
        model = Room
        fields = (
            "id",
            "home",
            "home_id",
            "name",
            "description",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "home", "created_at", "updated_at")

    def validate(self, attrs):
        request = self.context.get("request")
        home = attrs.get("home") or getattr(self.instance, "home", None)
        if (
            request
            and home
            and not user_has_home_access(
                request.user, home, write=request.method not in SAFE_METHODS
            )
        ):
            raise serializers.ValidationError(
                {"home_id": "You do not have permission to manage rooms in this home."}
            )
        return attrs


class RoomSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ("id", "name", "description")


class DeviceSerializer(serializers.ModelSerializer):
    home = serializers.PrimaryKeyRelatedField(read_only=True)
    home_id = serializers.PrimaryKeyRelatedField(
        source="home", queryset=Home.objects.all(), write_only=True
    )
    room = RoomSummarySerializer(read_only=True)
    room_id = serializers.PrimaryKeyRelatedField(
        source="room",
        queryset=Room.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Device
        fields = (
            "id",
            "home",
            "home_id",
            "room",
            "room_id",
            "name",
            "device_type",
            "hardware_id",
            "status",
            "is_active",
            "current_state",
            "state_payload",
            "certificate_fingerprint",
            "last_seen_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "home",
            "room",
            "status",
            "last_seen_at",
            "created_at",
            "updated_at",
        )

    def validate(self, attrs):
        request = self.context.get("request")
        home = attrs.get("home") or getattr(self.instance, "home", None)
        room = attrs.get("room")
        if room is None and self.instance is not None:
            room = self.instance.room

        if home and room and room.home_id != home.id:
            raise serializers.ValidationError(
                {"room_id": "Selected room does not belong to this home."}
            )

        if request and home and not request.user.is_superuser:
            if home.owner_id != request.user.id:
                membership = home.memberships.filter(user=request.user).first()
                if membership is None or not membership.can_manage_devices:
                    raise serializers.ValidationError(
                        {
                            "home_id": "You do not have permission to manage devices in this home."
                        }
                    )
        return attrs


class SensorDataSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source="device.name", read_only=True)

    class Meta:
        model = SensorData
        fields = (
            "id",
            "device",
            "device_name",
            "metric_name",
            "value",
            "unit",
            "payload",
            "source",
            "timestamp",
        )
        read_only_fields = ("id", "timestamp", "device_name", "device")


class SensorDataCreateSerializer(serializers.Serializer):
    metric_name = serializers.CharField(max_length=50)
    value = serializers.FloatField(required=False, allow_null=True)
    unit = serializers.CharField(max_length=20, required=False, allow_blank=True)
    payload = serializers.JSONField(required=False, default=dict)


class DeviceActionSerializer(serializers.ModelSerializer):
    user = PublicUserSerializer(read_only=True)

    class Meta:
        model = DeviceAction
        fields = (
            "id",
            "device",
            "user",
            "action_type",
            "payload",
            "status",
            "correlation_id",
            "source",
            "timestamp",
        )
        read_only_fields = (
            "id",
            "device",
            "user",
            "status",
            "correlation_id",
            "source",
            "timestamp",
        )


class DeviceCommandCreateSerializer(serializers.Serializer):
    action_type = serializers.CharField(max_length=50)
    payload = serializers.JSONField(required=False, default=dict)
