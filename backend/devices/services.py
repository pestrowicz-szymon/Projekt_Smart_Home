import json
from datetime import timedelta
from uuid import uuid4

from django.db import connection, transaction
from django.utils import timezone

from .models import Device, DeviceAction, Gateway, SensorData


def build_gateway_heartbeat_topic(gateway_cn: str) -> str:
    return f"gateways/{gateway_cn}/heartbeat"


def build_device_heartbeat_topic(gateway_cn: str, hardware_id: str) -> str:
    return f"gateways/{gateway_cn}/devices/{hardware_id}/heartbeat"


def build_gateway_announce_topic(gateway_cn: str) -> str:
    return f"gateways/{gateway_cn}/announce"


def build_telemetry_topic(gateway_cn: str, hardware_id: str) -> str:
    return f"gateways/{gateway_cn}/devices/{hardware_id}/telemetry"


def build_command_topic(gateway_cn: str, hardware_id: str) -> str:
    return f"gateways/{gateway_cn}/devices/{hardware_id}/commands"


def build_command_ack_topic(gateway_cn: str, hardware_id: str) -> str:
    return f"gateways/{gateway_cn}/devices/{hardware_id}/commands/ack"


def notify_device_update(home_id: int | None, data: dict):
    """
    Broadcasting device updates via PostgreSQL NOTIFY.
    """
    if home_id is None:
        return

    channel = f"home_{home_id}_updates"
    payload = json.dumps(data)
    with connection.cursor() as cursor:
        cursor.execute(f"NOTIFY {channel}, %s", [payload])


def notify_device_created(device: Device):
    """
    Notify subscribers about a new device being added to a home.
    """
    if not device.home:
        return

    from .serializers import DeviceSerializer

    data = {
        "type": "device_created",
        "device": DeviceSerializer(device).data,
    }
    notify_device_update(device.home.id, data)


@transaction.atomic
def record_sensor_reading(
    *,
    device: Device,
    metric_name: str,
    value=None,
    unit: str = "",
    payload: dict | None = None,
    source: str = "mqtt",
) -> SensorData:
    reading = SensorData.objects.create(
        device=device,
        metric_name=metric_name,
        value=value,
        unit=unit,
        payload=payload or {},
        source=source,
    )

    device.last_seen_at = timezone.now()
    device.status = Device.Status.ONLINE
    if value is not None:
        device.current_state = value
    if payload:
        device.state_payload = payload
    device.save(
        update_fields=[
            "last_seen_at",
            "status",
            "current_state",
            "state_payload",
            "updated_at",
        ]
    )

    # Notify subscribers
    notify_device_update(
        device.home.id if device.home else None,
        {
            "type": "device_update",
            "device_id": device.id,
            "current_state": device.current_state,
            "state_payload": device.state_payload,
            "last_seen_at": device.last_seen_at.isoformat()
            if device.last_seen_at
            else None,
            "status": device.status,
        },
    )

    return reading


def check_heartbeats(threshold_seconds: int = 30):
    """
    Checks for gateways and devices that haven't been seen recently and marks them offline.
    """
    now = timezone.now()
    cutoff = now - timedelta(seconds=threshold_seconds)

    # 1. Check Gateways
    inactive_gateways = Gateway.objects.filter(
        status=Gateway.Status.ONLINE, last_seen_at__lt=cutoff
    )
    for gateway in inactive_gateways:
        gateway.status = Gateway.Status.OFFLINE
        gateway.save(update_fields=["status", "updated_at"])

    # 2. Check Devices
    inactive_devices = Device.objects.filter(
        status=Device.Status.ONLINE, last_seen_at__lt=cutoff
    )
    for device in inactive_devices:
        device.status = Device.Status.OFFLINE
        device.save(update_fields=["status", "updated_at"])

        # Notify frontend
        notify_device_update(
            device.home.id if device.home else None,
            {
                "type": "device_update",
                "device_id": device.id,
                "current_state": device.current_state,
                "state_payload": device.state_payload,
                "last_seen_at": device.last_seen_at.isoformat()
                if device.last_seen_at
                else None,
                "status": device.status,
            },
        )

    return inactive_gateways.count(), inactive_devices.count()


@transaction.atomic
def enqueue_device_action(
    *,
    device: Device,
    action_type: str,
    user=None,
    payload: dict | None = None,
    source: str = "api",
) -> DeviceAction:
    return DeviceAction.objects.create(
        device=device,
        user=user if getattr(user, "is_authenticated", False) else None,
        action_type=action_type,
        payload=payload or {},
        status=DeviceAction.Status.PENDING,
        correlation_id=uuid4().hex,
        source=source,
    )


def mark_action_sent(action: DeviceAction) -> DeviceAction:
    action.status = DeviceAction.Status.SENT
    action.save(update_fields=["status"])
    return action


@transaction.atomic
def mark_action_acked(action: DeviceAction) -> DeviceAction:
    action.status = DeviceAction.Status.ACKED
    action.save(update_fields=["status"])

    # Update the device state based on the action that was just acked
    device = action.device
    if action.action_type in ["turn_on", "unlock"]:
        device.current_state = 1.0
    elif action.action_type in ["turn_off", "lock"]:
        device.current_state = 0.0

    device.save(update_fields=["current_state", "updated_at"])

    # Notify subscribers about action success
    notify_device_update(
        device.home.id if device.home else None,
        {
            "type": "action_acked",
            "device_id": device.id,
            "action_id": action.id,
            "correlation_id": action.correlation_id,
            "status": action.status,
        },
    )

    # Also notify about the device state change
    notify_device_update(
        device.home.id if device.home else None,
        {
            "type": "device_update",
            "device_id": device.id,
            "current_state": device.current_state,
            "state_payload": device.state_payload,
            "last_seen_at": device.last_seen_at.isoformat()
            if device.last_seen_at
            else None,
            "status": device.status,
        },
    )

    return action


def mark_action_failed(action: DeviceAction) -> DeviceAction:
    action.status = DeviceAction.Status.FAILED
    action.save(update_fields=["status"])

    # Notify subscribers about action failure
    notify_device_update(
        action.device.home.id if action.device.home else None,
        {
            "type": "action_failed",
            "device_id": action.device.id,
            "action_id": action.id,
            "correlation_id": action.correlation_id,
            "status": action.status,
        },
    )

    return action
