import logging
import random
from abc import ABC, abstractmethod
from typing import Any, Dict

logger = logging.getLogger(__name__)


class DeviceSimulator(ABC):
    """Base class for all simulated devices connected to the Gateway."""

    def __init__(self, gateway, hardware_id: str, name: str, device_type: str):
        self.gateway = gateway
        self.hardware_id = hardware_id
        self.name = name
        self.device_type = device_type
        self.current_state = 0.0
        self.state_payload: Dict[str, Any] = {}

    @abstractmethod
    def step(self):
        """Update internal state."""
        pass

    def handle_command(self, action_type: str, payload: Dict[str, Any]):
        """Respond to incoming MQTT commands."""
        logger.info(f"[{self.name}] Received command: {action_type}")
        if action_type in ["turn_on", "unlock"]:
            self.current_state = 1.0
        elif action_type in ["turn_off", "lock"]:
            self.current_state = 0.0

    def get_telemetry(self) -> Dict[str, Any]:
        return {
            "metric_name": self.get_metric_name(),
            "value": self.current_state,
            "device_type": self.device_type,
            "name": self.name,
            "payload": self.state_payload,
        }

    @abstractmethod
    def get_metric_name(self) -> str:
        pass


class Thermometer(DeviceSimulator):
    def __init__(self, gateway, hardware_id: str, name: str):
        super().__init__(gateway, hardware_id, name, "thermometer")
        self.current_state = 21.0

    def step(self):
        # Random walk for temperature
        self.current_state += 0.1 * random.random() * random.choice([-1, 1])
        self.current_state = round(self.current_state, 2)

    def get_metric_name(self) -> str:
        return "temperature"


class Light(DeviceSimulator):
    def __init__(self, gateway, hardware_id: str, name: str):
        super().__init__(gateway, hardware_id, name, "light")

    def step(self):
        pass  # State only changes via commands

    def get_metric_name(self) -> str:
        return "status"


class Lock(DeviceSimulator):
    def __init__(self, gateway, hardware_id: str, name: str):
        super().__init__(gateway, hardware_id, name, "lock")

    def step(self):
        pass  # State only changes via commands

    def get_metric_name(self) -> str:
        return "locked"


class SmokeDetector(DeviceSimulator):
    def __init__(self, gateway, hardware_id: str, name: str):
        super().__init__(gateway, hardware_id, name, "smoke_detector")
        self.current_state = 0.0  # 0.0 = Clear, 1.0 = Smoke Detected

    def step(self):
        # Very low chance of triggering smoke in a simulator
        if random.random() < 0.001:
            self.current_state = 1.0
        elif self.current_state == 1.0 and random.random() < 0.1:
            self.current_state = 0.0  # Clear smoke after a while

    def get_metric_name(self) -> str:
        return "smoke_level"
