import asyncio
import json
import logging
import os
import random
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
import paho.mqtt.client as mqtt
import pyotp


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

API_URL = os.getenv("API_URL", "http://localhost:8000/api")
USERNAME = os.getenv("USERNAME", "admin")
PASSWORD = os.getenv("PASSWORD", "admin")
MFA_SECRET = os.getenv("MFA_SECRET", "")
UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", "5"))
BATTERY_DRAIN_INTERVAL = int(os.getenv("BATTERY_DRAIN_INTERVAL", "60"))

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "8883"))
MQTT_USE_TLS = os.getenv("MQTT_USE_TLS", "true").lower() in {"1", "true", "yes"}

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DeviceSimulator(ABC):
    """Base class for all simulated devices."""

    def __init__(self, simulator, device_data: Dict[str, Any]):
        self.simulator = simulator
        self.id = device_data["id"]
        self.name = device_data["name"]
        self.device_type = device_data["device_type"]
        self.hardware_id = device_data["hardware_id"]

        # Backend returns home object, we need its ID for topic construction
        self.home_id = (
            device_data["home"]["id"]
            if isinstance(device_data.get("home"), dict)
            else device_data.get("home_id")
        )

        self.state_payload = device_data.get("state_payload") or {}
        self.current_state = device_data.get("current_state") or 0.0
        self.battery = self.state_payload.get("battery", 100)
        self.last_battery_update = time.time()

    @abstractmethod
    async def step(self):
        """Perform one simulation step (logic + telemetry)."""
        pass

    def handle_command(self, action_type: str, payload: Dict[str, Any]):
        """Respond to incoming MQTT commands."""
        logger.info(f"[{self.name}] Received command: {action_type}")
        if action_type in ["turn_on", "unlock"]:
            self.current_state = 1.0
        elif action_type in ["turn_off", "lock"]:
            self.current_state = 0.0

    async def report_telemetry(self, metric: str, value: Any, unit: str = ""):
        """Report data via MQTT (tests the backend MQTT bridge)."""
        topic = f"homes/{self.home_id}/devices/{self.hardware_id}/telemetry"
        payload = {
            "metric_name": metric,
            "value": value,
            "unit": unit,
            "payload": {**self.state_payload, "battery": self.battery},
        }
        self.simulator.mqtt_client.publish(topic, json.dumps(payload), qos=1)

    async def update_battery(self):
        now = time.time()
        if now - self.last_battery_update >= BATTERY_DRAIN_INTERVAL:
            if self.battery > 0:
                self.battery -= 1
                self.state_payload["battery"] = self.battery
            self.last_battery_update = now


class Thermometer(DeviceSimulator):
    async def step(self):
        # Random walk for temperature
        self.current_state += (
            0.1 * random.binomialvariate(1, 0.05) * (-1) ** random.choice([0, 1])
        )
        self.current_state = round(self.current_state, 2)
        await self.report_telemetry("temperature", self.current_state, "°C")


class SmokeDetector(DeviceSimulator):
    async def step(self):
        if self.current_state == 0:
            if random.random() > 0.995:
                self.current_state = 1.0
                logger.warning(f"[{self.name}] !!! SMOKE DETECTED !!!")
        else:
            if random.random() > 0.9:
                self.current_state = 0.0
                logger.info(f"[{self.name}] Smoke cleared.")

        await self.report_telemetry("smoke_level", self.current_state)


class GenericActuator(DeviceSimulator):
    async def step(self):
        # Actuators just report their current state (usually changed via MQTT)
        await self.report_telemetry("status", self.current_state)


class SmartHomeSimulator:
    def __init__(self):
        self.token: Optional[str] = None
        self.client = httpx.AsyncClient(base_url=API_URL, timeout=10.0)
        self.mqtt_client: Optional[mqtt.Client] = None
        self.devices: Dict[str, DeviceSimulator] = {}
        self.running = True

    async def login(self) -> bool:
        """Authenticated login with support for MFA."""
        logger.info(f"Logging in as {USERNAME}...")
        try:
            # 1. First stage: Username/Password
            resp = await self.client.post(
                "/users/login/", json={"username": USERNAME, "password": PASSWORD}
            )

            if resp.status_code != 200:
                logger.error(f"Login failed: {resp.text}")
                return False

            data = resp.json()

            # 2. Handle MFA if required
            if data.get("mfa_required"):
                if not MFA_SECRET:
                    logger.error(
                        "MFA required by backend but MFA_SECRET not set in .env"
                    )
                    return False

                totp = pyotp.TOTP(MFA_SECRET)
                mfa_code = totp.now()
                logger.info(f"MFA required. Sending TOTP code: {mfa_code}")

                resp = await self.client.post(
                    "/users/login/",
                    json={"mfa_token": data["mfa_token"], "mfa_code": mfa_code},
                )

                if resp.status_code != 200:
                    logger.error(f"MFA verification failed: {resp.text}")
                    return False
                data = resp.json()

            self.token = data["access"]
            self.client.headers.update({"Authorization": f"Bearer {self.token}"})
            logger.info("Login successful (MFA verified).")
            return True

        except Exception as e:
            logger.exception("Connection error during login")
            return False

    def setup_mqtt(self):
        self.mqtt_client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2
        )
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message

        if MQTT_USE_TLS:
            sim_dir = Path(__file__).resolve().parent

            def resolve(p):
                return str(sim_dir / p) if p and not Path(p).is_absolute() else p

            self.mqtt_client.tls_set(
                ca_certs=resolve(os.getenv("MQTT_CA_CERTS")),
                certfile=resolve(os.getenv("MQTT_CLIENT_CERT")),
                keyfile=resolve(os.getenv("MQTT_CLIENT_KEY")),
            )
            # For self-signed certs in dev, we need to allow the certificate chain
            # but we can skip strict hostname verification.
            self.mqtt_client.tls_insecure_set(True)

        try:
            self.mqtt_client.connect(MQTT_HOST, MQTT_PORT)
            self.mqtt_client.loop_start()
        except Exception as e:
            logger.error(f"Could not connect to MQTT: {e}")
            # Don't crash the whole simulator if MQTT is temporarily down

    def on_mqtt_connect(self, client, userdata, flags, rc, props):
        logger.info("Connected to MQTT Broker")
        client.subscribe("homes/+/devices/+/commands")

    def on_mqtt_message(self, client, userdata, msg):
        try:
            topic_parts = msg.topic.split("/")
            hw_id = topic_parts[3]
            if hw_id in self.devices:
                payload = json.loads(msg.payload.decode())
                device = self.devices[hw_id]
                device.handle_command(
                    payload["action_type"], payload.get("payload", {})
                )

                # Send ACK
                ack_topic = f"homes/{topic_parts[1]}/devices/{hw_id}/commands/ack"
                self.mqtt_client.publish(
                    ack_topic,
                    json.dumps(
                        {
                            "correlation_id": payload["correlation_id"],
                            "status": "success",
                        }
                    ),
                )
        except Exception:
            logger.exception("Error handling MQTT command")

    async def fetch_devices(self):
        try:
            resp = await self.client.get("/devices/devices/")
            if resp.status_code == 401:
                await self.login()
                return await self.fetch_devices()
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"Failed to fetch devices: {e}")
            return []

    async def run(self):
        if not await self.login():
            return
        self.setup_mqtt()

        logger.info("IoT Simulator running. Press Ctrl+C to stop.")

        while self.running:
            # 1. Sync device list from backend
            api_devices = await self.fetch_devices()
            active_hw_ids = {d["hardware_id"] for d in api_devices}

            # 2. Add new devices
            for d in api_devices:
                hw_id = d["hardware_id"]
                if hw_id not in self.devices:
                    match d["device_type"]:
                        case "thermometer":
                            cls = Thermometer
                        case "smoke_detector":
                            cls = SmokeDetector
                        case _:
                            cls = GenericActuator
                    self.devices[hw_id] = cls(self, d)
                    logger.info(
                        f"Started simulation for: {d['name']} ({d['device_type']})"
                    )

            # 3. Cleanup removed devices
            self.devices = {
                hw_id: dev
                for hw_id, dev in self.devices.items()
                if hw_id in active_hw_ids
            }

            # 4. Simulation step for all devices
            for dev in list(self.devices.values()):
                await dev.update_battery()
                await dev.step()

            await asyncio.sleep(UPDATE_INTERVAL)


if __name__ == "__main__":
    simulator = SmartHomeSimulator()
    try:
        asyncio.run(simulator.run())
    except KeyboardInterrupt:
        logger.info("Shutdown requested.")
    finally:
        simulator.running = False
