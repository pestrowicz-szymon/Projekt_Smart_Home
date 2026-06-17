import json
import logging
import os
from dataclasses import dataclass
from typing import Any

from django.db import close_old_connections
from paho.mqtt import client as mqtt

from .models import Device, DeviceAction
from .services import (
    build_command_ack_topic,
    build_command_topic,
    build_telemetry_topic,
    mark_action_acked,
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

    # Helper to resolve paths relative to backend directory if they are relative
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
    client.tls_set(**tls_kwargs)
    # Set insecure to True to skip hostname verification (fixes 'localhost' vs certificate name mismatch)
    client.tls_insecure_set(True)


def _create_client(client_id: str | None = None) -> mqtt.Client:
    settings = _connection_settings()
    # Paho MQTT 2.0+ requires CallbackAPIVersion. We use version 2.
    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id=client_id or settings.client_id,
        protocol=mqtt.MQTTv311,
    )
    _configure_security(client, settings)
    return client


def _topic_parts(topic: str) -> list[str]:
    return topic.split("/")


def _handle_telemetry(topic: str, payload: dict[str, Any]) -> None:
    parts = _topic_parts(topic)
    if len(parts) != 5:
        logger.warning("Ignoring malformed telemetry topic: %s", topic)
        return

    _, home_id_str, _, hardware_id, channel = parts
    if channel != "telemetry":
        return

    try:
        home_id = int(home_id_str)
    except ValueError:
        logger.warning("Ignoring telemetry topic with invalid home id: %s", topic)
        return

    close_old_connections()
    device = (
        Device.objects.select_related("home")
        .filter(home_id=home_id, hardware_id=hardware_id)
        .first()
    )
    if device is None:
        logger.warning("No device found for telemetry topic %s", topic)
        return

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

    _, home_id_str, _, hardware_id, channel, suffix = parts
    if channel != "commands" or suffix != "ack":
        return

    try:
        home_id = int(home_id_str)
    except ValueError:
        logger.warning("Ignoring command ack topic with invalid home id: %s", topic)
        return

    correlation_id = payload.get("correlation_id")
    if not correlation_id:
        logger.warning("Ignoring command ack without correlation_id on topic %s", topic)
        return

    close_old_connections()
    action = (
        DeviceAction.objects.select_related("device", "device__home")
        .filter(
            device__home_id=home_id,
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

    # Use wildcards for initial subscription
    client.subscribe(build_telemetry_topic("+", "+"))
    client.subscribe(build_command_ack_topic("+", "+"))
    logger.info("Connected to MQTT broker and subscribed to telemetry and ack topics")


def _on_message(client: mqtt.Client, userdata: Any, message: mqtt.MQTTMessage) -> None:
    try:
        payload = json.loads(message.payload.decode("utf-8"))
    except json.JSONDecodeError:
        logger.exception("Received invalid JSON payload on topic %s", message.topic)
        return

    if message.topic.endswith("/telemetry"):
        _handle_telemetry(message.topic, payload)
    elif message.topic.endswith("/commands/ack"):
        _handle_command_ack(message.topic, payload)
    else:
        logger.debug("Ignoring message on unsupported topic %s", message.topic)


def publish_device_action(action: DeviceAction) -> None:
    settings = _connection_settings()
    client = _create_client(client_id=f"{settings.client_id}-publisher")
    client.connect(settings.host, settings.port, settings.keepalive)
    client.loop_start()
    payload = {
        "correlation_id": action.correlation_id,
        "home_id": action.device.home.id,
        "device_id": action.device.id,
        "hardware_id": action.device.hardware_id,
        "action_type": action.action_type,
        "payload": action.payload,
    }
    info = client.publish(
        build_command_topic(action.device.home.id, action.device.hardware_id),
        json.dumps(payload),
        qos=1,
    )
    info.wait_for_publish()
    client.loop_stop()
    client.disconnect()
    logger.info(
        "Published MQTT action %s for device %s",
        action.correlation_id,
        action.device.hardware_id,
    )


def run_mqtt_bridge() -> None:
    settings = _connection_settings()
    client = _create_client()
    client.on_connect = _on_connect
    client.on_message = _on_message
    client.connect(settings.host, settings.port, settings.keepalive)
    logger.info("Starting MQTT bridge against %s:%s", settings.host, settings.port)
    client.loop_forever()
