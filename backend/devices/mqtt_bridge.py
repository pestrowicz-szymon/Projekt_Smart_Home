import json
import logging
import os
import ssl
from dataclasses import dataclass
from typing import Any

from django.db import close_old_connections
from django.utils import timezone
from paho.mqtt import client as mqtt

from .models import Device, DeviceAction, Gateway
from .services import (
    build_command_ack_topic,
    build_command_topic,
    build_device_heartbeat_topic,
    build_gateway_announce_topic,
    build_gateway_heartbeat_topic,
    build_telemetry_topic,
    mark_action_acked,
    notify_device_created,
    record_sensor_reading,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MQTTConnectionSettings:
    host: str = os.getenv("MQTT_HOST", "mosquitto")
    port: int = int(os.getenv("MQTT_PORT", "8883"))
    client_id: str = os.getenv("MQTT_CLIENT_ID", "smart-home-backend")
    username: str | None = os.getenv("MQTT_USERNAME")
    password: str | None = os.getenv("MQTT_PASSWORD")
    use_tls: bool = os.getenv("MQTT_USE_TLS", "true").lower() in {"1", "true", "yes"}
    ca_certs: str | None = os.getenv("MQTT_CA_CERTS")
    client_cert: str | None = os.getenv("MQTT_CLIENT_CERT")
    client_key: str | None = os.getenv("MQTT_CLIENT_KEY")
    keepalive: int = int(os.getenv("MQTT_KEEPALIVE", "60"))


def _connection_settings() -> MQTTConnectionSettings:
    return MQTTConnectionSettings()


def _configure_security(client: mqtt.Client, settings: MQTTConnectionSettings) -> None:
    if settings.username:
        client.username_pw_set(settings.username, settings.password)

    if not settings.use_tls:
        return

    tls_kwargs: dict[str, Any] = {}

    from pathlib import Path

    backend_dir = Path(__file__).resolve().parent.parent

    def resolve_path(p: str | None) -> str | None:
        if not p:
            return None
        path = Path(p)
        if not path.is_absolute():
            return str(backend_dir / path)
        return str(path)

    if settings.ca_certs:
        tls_kwargs["ca_certs"] = resolve_path(settings.ca_certs)
    if settings.client_cert:
        tls_kwargs["certfile"] = resolve_path(settings.client_cert)
    if settings.client_key:
        tls_kwargs["keyfile"] = resolve_path(settings.client_key)

    logger.debug("MQTT TLS Config: %s", tls_kwargs)
    tls_kwargs["cert_reqs"] = ssl.CERT_REQUIRED
    client.tls_set(**tls_kwargs)
    client.tls_insecure_set(False)


def _create_client(client_id: str | None = None) -> mqtt.Client:
    settings = _connection_settings()
    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id=client_id or settings.client_id,
        protocol=mqtt.MQTTv311,
    )
    _configure_security(client, settings)
    return client


def _topic_parts(topic: str) -> list[str]:
    return topic.split("/")


def _handle_announce(topic: str, payload: dict[str, Any]) -> None:
    logger.info("Handling announce on topic: %s", topic)
    parts = _topic_parts(topic)
    if len(parts) != 3:
        logger.warning("Malformed announce topic: %s", topic)
        return

    gateway_cn = parts[1]
    pairing_code = payload.get("pairing_code")
    close_old_connections()
    try:
        gateway, created = Gateway.objects.get_or_create(
            hardware_id=gateway_cn,
            defaults={
                "status": Gateway.Status.ONLINE,
                "last_seen_at": timezone.now(),
                "pairing_code": pairing_code,
            },
        )
        if not created:
            gateway.status = Gateway.Status.ONLINE
            gateway.last_seen_at = timezone.now()
            update_fields = ["status", "last_seen_at", "updated_at"]
            if pairing_code and gateway.home is None:
                gateway.pairing_code = pairing_code
                update_fields.append("pairing_code")
            gateway.save(update_fields=update_fields)

        logger.info(
            "Gateway announcement processed: %s (created: %s)", gateway_cn, created
        )
    except Exception:
        logger.exception("Error processing gateway announcement")


def _handle_heartbeat(topic: str, payload: dict[str, Any]) -> None:
    logger.debug("Handling heartbeat on topic: %s", topic)
    parts = _topic_parts(topic)

    # gateways/{gateway_cn}/heartbeat -> len 3
    # gateways/{gateway_cn}/devices/{hw_id}/heartbeat -> len 5

    close_old_connections()
    if len(parts) == 3:
        gateway_cn = parts[1]
        Gateway.objects.filter(hardware_id=gateway_cn).update(
            status=Gateway.Status.ONLINE,
            last_seen_at=timezone.now(),
            updated_at=timezone.now(),
        )
    elif len(parts) == 5:
        gateway_cn = parts[1]
        hardware_id = parts[3]
        Device.objects.filter(
            gateway__hardware_id=gateway_cn, hardware_id=hardware_id
        ).update(
            status=Device.Status.ONLINE,
            last_seen_at=timezone.now(),
            updated_at=timezone.now(),
        )


def _handle_telemetry(topic: str, payload: dict[str, Any]) -> None:
    logger.debug("Handling telemetry on topic: %s", topic)
    parts = _topic_parts(topic)
    if len(parts) != 5:
        logger.warning("Ignoring malformed telemetry topic: %s", topic)
        return

    _, gateway_cn, _, hardware_id, channel = parts
    if channel != "telemetry":
        return

    close_old_connections()
    gateway = Gateway.objects.filter(hardware_id=gateway_cn).first()
    if gateway is None:
        logger.warning("No gateway found for telemetry topic %s", topic)
        return

    device = (
        Device.objects.select_related("home")
        .filter(gateway=gateway, hardware_id=hardware_id)
        .first()
    )
    if device is None:
        # Auto-register device if linked to a known gateway
        device = Device.objects.create(
            gateway=gateway,
            home=gateway.home,
            hardware_id=hardware_id,
            name=payload.get("name", f"Unknown {hardware_id}"),
            device_type=payload.get("device_type", "generic_sensor"),
            status=Device.Status.ONLINE,
        )
        logger.info("Auto-registered device %s for gateway %s", hardware_id, gateway_cn)
        notify_device_created(device)

    record_sensor_reading(
        device=device,
        metric_name=payload.get("metric_name", "value"),
        value=payload.get("value"),
        unit=payload.get("unit", ""),
        payload=payload.get("payload", payload),
        source="mqtt",
    )


def _handle_command_ack(topic: str, payload: dict[str, Any]) -> None:
    parts = _topic_parts(topic)
    if len(parts) != 6:
        logger.warning("Ignoring malformed command ack topic: %s", topic)
        return

    _, gateway_cn, _, hardware_id, channel, suffix = parts
    if channel != "commands" or suffix != "ack":
        return

    correlation_id = payload.get("correlation_id")
    if not correlation_id:
        logger.warning("Ignoring command ack without correlation_id on topic %s", topic)
        return

    close_old_connections()
    action = (
        DeviceAction.objects.select_related("device", "device__gateway")
        .filter(
            device__gateway__hardware_id=gateway_cn,
            device__hardware_id=hardware_id,
            correlation_id=correlation_id,
        )
        .first()
    )
    if action is None:
        logger.warning("No action found for ack on topic %s", topic)
        return

    mark_action_acked(action)


def _on_connect(
    client: mqtt.Client, userdata: Any, flags: Any, reason_code: Any, properties: Any
) -> None:
    if getattr(reason_code, "is_failure", False):
        logger.error("MQTT connection failed: %s", reason_code)
        return

    # Subscribe to gateway-centric topics
    client.subscribe("gateways/+/announce")
    client.subscribe("gateways/+/heartbeat")
    client.subscribe("gateways/+/devices/+/telemetry")
    client.subscribe("gateways/+/devices/+/heartbeat")
    client.subscribe("gateways/+/devices/+/commands/ack")
    logger.info("Connected to MQTT broker and subscribed to gateway topics")


def _on_message(client: mqtt.Client, userdata: Any, message: mqtt.MQTTMessage) -> None:
    try:
        payload = json.loads(message.payload.decode("utf-8"))
    except json.JSONDecodeError:
        logger.exception("Received invalid JSON payload on topic %s", message.topic)
        return

    if message.topic.endswith("/announce"):
        _handle_announce(message.topic, payload)
    elif message.topic.endswith("/heartbeat"):
        _handle_heartbeat(message.topic, payload)
    elif message.topic.endswith("/telemetry"):
        _handle_telemetry(message.topic, payload)
    elif message.topic.endswith("/commands/ack"):
        _handle_command_ack(message.topic, payload)
    else:
        logger.debug("Ignoring message on unsupported topic %s", message.topic)


def publish_device_action(action: DeviceAction) -> None:
    if not action.device.gateway:
        logger.error(
            "Cannot publish action for device %s: No gateway assigned",
            action.device.hardware_id,
        )
        return

    settings = _connection_settings()
    client = _create_client(client_id=f"{settings.client_id}-publisher")
    client.connect(settings.host, settings.port, settings.keepalive)
    client.loop_start()

    payload = {
        "correlation_id": action.correlation_id,
        "hardware_id": action.device.hardware_id,
        "action_type": action.action_type,
        "payload": action.payload,
    }

    topic = build_command_topic(
        action.device.gateway.hardware_id, action.device.hardware_id
    )
    info = client.publish(
        topic,
        json.dumps(payload),
        qos=1,
    )
    info.wait_for_publish()
    client.loop_stop()
    client.disconnect()
    logger.info(
        "Published MQTT action %s for device %s on topic %s",
        action.correlation_id,
        action.device.hardware_id,
        topic,
    )


def run_mqtt_bridge() -> None:
    settings = _connection_settings()
    client = _create_client()
    client.on_connect = _on_connect
    client.on_message = _on_message
    client.connect(settings.host, settings.port, settings.keepalive)
    logger.info("Starting MQTT bridge against %s:%s", settings.host, settings.port)
    client.loop_forever()
