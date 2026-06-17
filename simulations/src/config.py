from models import Light, Lock, SmokeDetector, Thermometer


def get_devices(gateway):
    """
    Returns a dictionary of initialized devices for the given gateway.
    """
    return {
        "temp-01": Thermometer(gateway, "temp-01", "Living Room Temp"),
        "light-01": Light(gateway, "light-01", "Kitchen Light"),
        "lock-01": Lock(gateway, "lock-01", "Front Door"),
        "smoke-01": SmokeDetector(gateway, "smoke-01", "Hallway Smoke Detector"),
        "smoke-02": SmokeDetector(gateway, "smoke-02", "Kitchen Smoke Detector"),
        # "smoke-03": SmokeDetector(gateway, "smoke-03", "Kitchen Smoke Detector"),
    }
