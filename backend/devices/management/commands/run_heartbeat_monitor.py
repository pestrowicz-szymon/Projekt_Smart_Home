import logging
import time

from django.core.management.base import BaseCommand

from devices.services import check_heartbeats

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Periodically checks for inactive gateways and devices and marks them offline."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--interval",
            type=int,
            default=10,
            help="Interval in seconds between checks (default: 10)",
        )
        parser.add_argument(
            "--threshold",
            type=int,
            default=15,
            help="Inactivity threshold in seconds (default: 15)",
        )

    def handle(self, *args, **options):
        interval = options["interval"]
        threshold = options["threshold"]

        self.stdout.write(
            self.style.SUCCESS(
                f"Starting heartbeat monitor (interval={interval}s, threshold={threshold}s)"
            )
        )

        try:
            while True:
                gw_count, dev_count = check_heartbeats(threshold_seconds=threshold)
                if gw_count > 0 or dev_count > 0:
                    self.stdout.write(
                        f"Heartbeat check: {gw_count} gateways and {dev_count} devices marked offline"
                    )
                time.sleep(interval)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Heartbeat monitor stopped."))
