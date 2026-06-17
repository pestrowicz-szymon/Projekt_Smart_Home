import asyncio
import json
import logging
import os
import random
from pathlib import Path
from typing import Any, Dict, Optional

import paho.mqtt.client as mqtt

from config import get_devices
from models import DeviceSimulator


# Simple .env loader
def load_env(file_path=".env"):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if "=" in line:
                        key, value = line.split("=", 1)
                        os.environ[key.strip()] = value.strip()


# Load configuration
load_env()

GATEWAY_CN = os.getenv("GATEWAY_CN", "gateway-001")
UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", "5"))

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "8883"))
MQTT_USE_TLS = os.getenv("MQTT_USE_TLS", "true").lower() in {"1", "true", "yes"}

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SmartGatewaySimulator:
    def __init__(self):
        self.gateway_cn = GATEWAY_CN
        self.pairing_code = f"{random.randint(0, 999999):06d}"
        self.mqtt_client: Optional[mqtt.Client] = None
        self.devices: Dict[str, DeviceSimulator] = get_devices(self)
        self.running = True

    def setup_mqtt(self):
        self.mqtt_client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=f"gateway-sim-{self.gateway_cn}",
        )
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message

        if MQTT_USE_TLS:

            def resolve(p):
                if not p:
                    return None
                path = Path(p)
                if path.is_absolute():
                    return str(path)
                # For development, we still support relative paths to the simulator dir
                return str(Path(__file__).resolve().parent / path)

            ca_certs = resolve(os.getenv("MQTT_CA_CERTS"))
            certfile = resolve(os.getenv("MQTT_CLIENT_CERT"))
            keyfile = resolve(os.getenv("MQTT_CLIENT_KEY"))

            logger.info(f"Using mTLS. Cert: {certfile}")

            self.mqtt_client.tls_set(
                ca_certs=ca_certs,
                certfile=certfile,
                keyfile=keyfile,
            )
            self.mqtt_client.tls_insecure_set(True)

        try:
            self.mqtt_client.connect(MQTT_HOST, MQTT_PORT)
            self.mqtt_client.loop_start()
        except Exception as e:
            logger.error(f"Could not connect to MQTT: {e}")

    def on_mqtt_connect(self, client, userdata, flags, rc, props):
        if rc == 0:
            logger.info(f"Connected to MQTT Broker as {self.gateway_cn}")
            # Subscribe to commands for any of our devices
            client.subscribe(f"gateways/{self.gateway_cn}/devices/+/commands")
            # Send announcement
            self.announce()
        else:
            logger.error(f"Failed to connect to MQTT: {rc}")

    def on_mqtt_message(self, client, userdata, msg):
        try:
            # gateways/{gateway_cn}/devices/{hw_id}/commands
            parts = msg.topic.split("/")
            if len(parts) < 5:
                return

            hw_id = parts[3]
            if hw_id in self.devices:
                payload = json.loads(msg.payload.decode())
                device = self.devices[hw_id]
                device.handle_command(
                    payload["action_type"], payload.get("payload", {})
                )

                # Send ACK
                ack_topic = f"gateways/{self.gateway_cn}/devices/{hw_id}/commands/ack"
                self.mqtt_client.publish(
                    ack_topic,
                    json.dumps(
                        {
                            "correlation_id": payload["correlation_id"],
                            "status": "success",
                        }
                    ),
                    qos=1,
                )
        except Exception:
            logger.exception("Error handling MQTT command")

    def announce(self):
        topic = f"gateways/{self.gateway_cn}/announce"
        payload = {
            "firmware": "2.0.0-mtls",
            "model": "Simulated Gateway Pro",
            "device_count": len(self.devices),
            "pairing_code": self.pairing_code,
        }
        self.mqtt_client.publish(topic, json.dumps(payload), qos=1, retain=True)
        logger.info(f"Sent gateway announcement on {topic}")

    async def run(self):
        self.setup_mqtt()

        logger.info("*" * 40)
        logger.info(f"PAIRING PIN: {self.pairing_code}")
        logger.info("*" * 40)

        logger.info(
            f"Gateway Simulator ({self.gateway_cn}) running. Press Ctrl+C to stop."
        )

        heartbeat_interval = 5
        last_heartbeat = 0

        while self.running:
            now = asyncio.get_event_loop().time()

            # Send Heartbeats every 5 seconds
            if now - last_heartbeat >= heartbeat_interval:
                # Gateway heartbeat
                gw_hb_topic = f"gateways/{self.gateway_cn}/heartbeat"
                self.mqtt_client.publish(
                    gw_hb_topic, json.dumps({"status": "alive"}), qos=1
                )

                # Device heartbeats
                for hw_id in self.devices:
                    dev_hb_topic = (
                        f"gateways/{self.gateway_cn}/devices/{hw_id}/heartbeat"
                    )
                    self.mqtt_client.publish(
                        dev_hb_topic, json.dumps({"status": "alive"}), qos=1
                    )

                last_heartbeat = now
                logger.debug("Sent heartbeats for gateway and devices")

            for hw_id, dev in self.devices.items():
                dev.step()

                # Publish telemetry
                topic = f"gateways/{self.gateway_cn}/devices/{hw_id}/telemetry"
                payload = dev.get_telemetry()
                self.mqtt_client.publish(topic, json.dumps(payload), qos=1)

            await asyncio.sleep(UPDATE_INTERVAL)


if __name__ == "__main__":
    simulator = SmartGatewaySimulator()
    try:
        asyncio.run(simulator.run())
    except KeyboardInterrupt:
        logger.info("Shutdown requested.")
    finally:
        simulator.running = False
