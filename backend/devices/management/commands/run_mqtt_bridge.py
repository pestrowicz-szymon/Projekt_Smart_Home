from django.core.management.base import BaseCommand

from devices.mqtt_bridge import run_mqtt_bridge


class Command(BaseCommand):
	help = 'Run the MQTT bridge that connects device telemetry and command topics to the database.'

	def handle(self, *args, **options):
		try:
			run_mqtt_bridge()
		except KeyboardInterrupt:
			self.stdout.write(self.style.WARNING('MQTT bridge stopped.'))