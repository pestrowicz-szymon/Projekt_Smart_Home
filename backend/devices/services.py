import json
from uuid import uuid4

from django.db import connection, transaction
from django.utils import timezone

from .models import Device, DeviceAction, SensorData


def build_telemetry_topic(home_id: int | str, hardware_id: str) -> str:
    return f"homes/{home_id}/devices/{hardware_id}/telemetry"


def build_command_topic(home_id: int | str, hardware_id: str) -> str:
    return f"homes/{home_id}/devices/{hardware_id}/commands"


def build_command_ack_topic(home_id: int | str, hardware_id: str) -> str:
    return f"homes/{home_id}/devices/{hardware_id}/commands/ack"


def notify_device_update(home_id: int, data: dict):
    """
    Broadcasting device updates via PostgreSQL NOTIFY.
    """
    channel = f"home_{home_id}_updates"
    payload = json.dumps(data)
    with connection.cursor() as cursor:
        # PostgreSQL channel names are identifiers, but we use a fixed pattern
        # to avoid injection. Payload is passed as a parameter.
        cursor.execute(f"NOTIFY {channel}, %s", [payload])


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
        device.home.id,
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


def mark_action_acked(action: DeviceAction) -> DeviceAction:
    action.status = DeviceAction.Status.ACKED
    action.save(update_fields=["status"])

    # Notify subscribers about action
    notify_device_update(
        action.device.home.id,
        {
            "type": "action_acked",
            "device_id": action.device.id,
            "action_id": action.id,
            "correlation_id": action.correlation_id,
            "status": action.status,
        },
    )

    return action


def mark_action_failed(action: DeviceAction) -> DeviceAction:
    action.status = DeviceAction.Status.FAILED
    action.save(update_fields=["status"])

    # Notify subscribers about action failure
    notify_device_update(
        action.device.home.id,
        {
            "type": "action_failed",
            "device_id": action.device.id,
            "action_id": action.id,
            "correlation_id": action.correlation_id,
            "status": action.status,
        },
    )

    return action
