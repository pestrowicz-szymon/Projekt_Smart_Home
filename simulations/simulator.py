import asyncio
import json
import logging
import os
import random
import time

import paho.mqtt.client as mqtt
import requests


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
UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", "5"))
BATTERY_DRAIN_INTERVAL = int(os.getenv("BATTERY_DRAIN_INTERVAL", "60"))

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class SmartHomeSimulator:
    def __init__(self):
        self.api_url = API_URL
        self.username = USERNAME
        self.password = PASSWORD
        self.access_token = None
        self.refresh_token = None
        self.device_tasks = {}  # hardware_id -> Task
        self.device_states = {}  # hardware_id -> dict with current state
        self.running = True
        self.mqtt_client = None

    async def login(self):
        logging.info(f"Logging in to {self.api_url} as {self.username}...")
        url = f"{self.api_url}/users/login/"

        def do_login():
            return requests.post(
                url,
                json={"username": self.username, "password": self.password},
                timeout=10,
            )

        try:
            response = await asyncio.to_thread(do_login)
            response.raise_for_status()
            data = response.json()
            self.access_token = data["access"]
            self.refresh_token = data["refresh"]
            logging.info("Login successful.")
            return True
        except Exception as e:
            logging.error(f"Login failed: {e}")
            return False

    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    async def fetch_devices(self):
        url = f"{self.api_url}/devices/devices/"

        def do_fetch():
            return requests.get(url, headers=self.get_headers(), timeout=10)

        try:
            response = await asyncio.to_thread(do_fetch)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Failed to fetch devices: {e}")
            if (
                isinstance(e, requests.exceptions.HTTPError)
                and e.response.status_code == 401
            ):
                await self.login()
            return []

    async def update_reading(
        self, device_id, metric_name, value, unit="", payload=None
    ):
        url = f"{self.api_url}/devices/devices/{device_id}/readings/"
        data = {
            "metric_name": metric_name,
            "value": value,
            "unit": unit,
            "payload": payload or {},
        }

        def do_update():
            return requests.post(url, json=data, headers=self.get_headers(), timeout=10)

        try:
            response = await asyncio.to_thread(do_update)
            response.raise_for_status()
            return True
        except Exception as e:
            logging.error(f"Failed to update reading for device {device_id}: {e}")
            return False

    async def patch_device(self, device_id, data):
        url = f"{self.api_url}/devices/devices/{device_id}/"

        def do_patch():
            return requests.patch(
                url, json=data, headers=self.get_headers(), timeout=10
            )

        try:
            response = await asyncio.to_thread(do_patch)
            response.raise_for_status()
            return True
        except Exception as e:
            logging.error(f"Failed to patch device {device_id}: {e}")
            return False

    def on_mqtt_connect(self, client, userdata, flags, reason_code, properties):
        logging.info(f"Connected to MQTT broker with result code: {reason_code}")
        client.subscribe("homes/+/devices/+/commands")

    def on_mqtt_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            topic_parts = msg.topic.split("/")
            # homes/{home_id}/devices/{hardware_id}/commands
            home_id = topic_parts[1]
            hardware_id = topic_parts[3]

            if hardware_id in self.device_states:
                action_type = payload.get("action_type")
                correlation_id = payload.get("correlation_id")

                logging.info(f"Received action {action_type} for {hardware_id}")

                # Update internal state based on action
                if action_type in ["turn_on", "unlock"]:
                    self.device_states[hardware_id]["current_state"] = 1.0
                elif action_type in ["turn_off", "lock"]:
                    self.device_states[hardware_id]["current_state"] = 0.0

                # Send ACK back to backend
                ack_topic = f"homes/{home_id}/devices/{hardware_id}/commands/ack"
                ack_payload = {"correlation_id": correlation_id, "status": "success"}
                client.publish(ack_topic, json.dumps(ack_payload))
                logging.info(f"Sent ACK for action {action_type} on {hardware_id}")

        except Exception as e:
            logging.error(f"Error handling MQTT message: {e}")

    async def simulate_device(self, device_data):
        device_id = device_data["id"]
        name = device_data["name"]
        device_type = device_data["device_type"]
        hardware_id = device_data["hardware_id"]

        logging.info(f"START simulation: {name} ({device_type}) [{hardware_id}]")

        state_payload = device_data.get("state_payload") or {}
        if not isinstance(state_payload, dict):
            state_payload = {}

        battery = state_payload.get("battery", 100)
        current_state = device_data.get("current_state") or 0.0

        # Initialize shared state
        self.device_states[hardware_id] = {"current_state": current_state}

        last_battery_update = time.time()

        try:
            while self.running:
                # Read from shared state (might have been updated by MQTT)
                current_state = self.device_states[hardware_id]["current_state"]

                match device_type:
                    case "thermometer":
                        current_state += (
                            0.1
                            * random.binomialvariate(1, 0.05)
                            * (-1) ** random.choice([0, 1])
                        )
                        # Update shared state back
                        self.device_states[hardware_id]["current_state"] = current_state

                        await self.update_reading(
                            device_id, "temperature", current_state, "°C"
                        )
                        await self.patch_device(
                            device_id, {"current_state": current_state}
                        )
                        logging.info(f"[{name}] Temperature: {current_state}°C")

                    case "smoke_detector":
                        if current_state == 0:
                            if random.random() > 0.995:
                                current_state = 1
                                self.device_states[hardware_id]["current_state"] = (
                                    current_state
                                )
                                await self.update_reading(
                                    device_id, "smoke_level", current_state
                                )
                                await self.patch_device(
                                    device_id, {"current_state": current_state}
                                )
                                logging.warning(f"[{name}] SMOKE DETECTED")
                            else:
                                logging.info(f"[{name}] smoke not detected")
                        elif random.random() > 0.9:
                            current_state = 0
                            self.device_states[hardware_id]["current_state"] = (
                                current_state
                            )
                            await self.update_reading(
                                device_id, "smoke_level", current_state
                            )
                            await self.patch_device(
                                device_id, {"current_state": current_state}
                            )
                            logging.warning(f"[{name}] smoke not detected anymore")
                        else:
                            logging.info(f"[{name}] SMOKE DETECTED")

                    case "generic_sensor":
                        val = random.normalvariate(0, 0.05)
                        current_state = round(max(0, min(current_state + val, 100)), 2)
                        self.device_states[hardware_id]["current_state"] = current_state
                        await self.update_reading(device_id, "value", current_state)
                        await self.patch_device(
                            device_id, {"current_state": current_state}
                        )
                        logging.info(f"[{name}] Value: {current_state}")

                    case "actuator" | "light" | "lock":
                        await self.update_reading(device_id, "status", current_state)
                        await self.patch_device(
                            device_id, {"current_state": current_state}
                        )
                        logging.info(
                            f"[{name}] {device_type.capitalize()} state: {current_state}"
                        )

                # Battery state
                now = time.time()
                if now - last_battery_update >= BATTERY_DRAIN_INTERVAL:
                    if battery > 0:
                        battery -= 1
                        state_payload["battery"] = battery
                        await self.patch_device(
                            device_id, {"state_payload": state_payload}
                        )
                        logging.info(f"⚡ [{name}] Battery: {battery}%")
                    last_battery_update = now

                await asyncio.sleep(UPDATE_INTERVAL + random.uniform(-1, 1))

        except asyncio.CancelledError:
            logging.info(f"STOP simulation: {name}")
            if hardware_id in self.device_states:
                del self.device_states[hardware_id]
        except Exception as e:
            logging.error(f"ERROR in {name} simulation: {e}")

    async def run(self):
        if not await self.login():
            logging.error("Initial login failed. Exiting.")
            return

        # Start MQTT client
        self.mqtt_client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2
        )
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message
        try:
            self.mqtt_client.connect(MQTT_HOST, MQTT_PORT)
            self.mqtt_client.loop_start()
            logging.info(f"MQTT client started, connected to {MQTT_HOST}:{MQTT_PORT}")
        except Exception as e:
            logging.error(f"Failed to connect to MQTT broker: {e}")
            # Continue anyway, telemetry might still work via REST

        logging.info("Starting Device Manager (searching for devices every 30s)...")

        try:
            while self.running:
                devices = await self.fetch_devices()
                if not devices:
                    logging.warning("No devices found or error fetching devices.")

                active_hw_ids = set()
                for dev in devices:
                    hw_id = dev["hardware_id"]
                    active_hw_ids.add(hw_id)

                    if hw_id not in self.device_tasks:
                        task = asyncio.create_task(self.simulate_device(dev))
                        self.device_tasks[hw_id] = task

                # Cleanup removed devices
                to_remove = []
                for hw_id in self.device_tasks:
                    if hw_id not in active_hw_ids:
                        self.device_tasks[hw_id].cancel()
                        to_remove.append(hw_id)

                for hw_id in to_remove:
                    del self.device_tasks[hw_id]

                await asyncio.sleep(30)

        except asyncio.CancelledError:
            self.running = False
            if self.mqtt_client:
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()
            for task in self.device_tasks.values():
                task.cancel()
            logging.info("Manager stopped.")


if __name__ == "__main__":
    simulator = SmartHomeSimulator()
    try:
        asyncio.run(simulator.run())
    except KeyboardInterrupt:
        logging.info("Shutting down simulator...")
        simulator.running = False
