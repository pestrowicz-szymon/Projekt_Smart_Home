import { browser } from '$app/environment';
import type { Device } from '$lib/types/device';

export type DeviceEvent =
	| {
			type: 'device_update';
			device_id: number;
			current_state: number;
			state_payload: Record<string, unknown>;
			last_seen_at: string | null;
			status: string;
	  }
	| {
			type: 'device_created';
			device: Device;
	  }
	| {
			type: 'action_acked';
			device_id: number;
			action_id: number;
			correlation_id: string;
			status: string;
	  }
	| {
			type: 'action_failed';
			device_id: number;
			action_id: number;
			correlation_id: string;
			status: string;
	  };

class DeviceStore {
	devices = $state<Device[]>([]);
	status = $state<'connected' | 'disconnected' | 'connecting'>('disconnected');

	private currentHomeId: number | null = null;
	private eventSource: EventSource | null = null;

	init(initialDevices: Device[], homeId: number) {
		this.devices = initialDevices;
		const newHomeId = homeId;
		if (browser) {
			if (this.status === 'disconnected') {
				this.currentHomeId = newHomeId;
				this.connect();
			} else if (newHomeId !== this.currentHomeId) {
				console.log('Home changed, reconnecting SSE');
				this.currentHomeId = newHomeId;
				this.disconnect();
				this.connect();
			}
		}
	}

	private disconnect() {
		if (this.eventSource) {
			this.eventSource.close();
			this.eventSource = null;
		}
		this.status = 'disconnected';
	}

	private connect() {
		this.status = 'connecting';
		this.eventSource = new EventSource('/api/events');

		this.eventSource.onopen = () => {
			this.status = 'connected';
			console.log('SSE connected');
		};

		this.eventSource.onmessage = (event) => {
			try {
				const data = JSON.parse(event.data) as DeviceEvent;
				this.handleEvent(data);
			} catch (err) {
				console.error('Failed to parse SSE event', err);
			}
		};

		this.eventSource.onerror = () => {
			if (this.status !== 'disconnected') {
				this.status = 'disconnected';
				if (this.eventSource) {
					this.eventSource.close();
					this.eventSource = null;
				}
				// Reconnect after 5 seconds
				setTimeout(() => this.connect(), 5000);
			}
		};
	}

	private handleEvent(event: DeviceEvent) {
		if (event.type === 'device_update') {
			this.updateDeviceState(event.device_id, {
				current_state: event.current_state,
				state_payload: event.state_payload,
				last_seen_at: event.last_seen_at,
				status: event.status as Device['status']
			});
		} else if (event.type === 'device_created') {
			this.addOrUpdateDevice(event.device);
		} else if (event.type === 'action_acked' || event.type === 'action_failed') {
			console.log(`Action ${event.type}:`, event.correlation_id);
		}
	}

	updateDeviceState(deviceId: number, updates: Partial<Device>) {
		const index = this.devices.findIndex((d) => d.id === deviceId);
		if (index !== -1) {
			this.devices[index] = {
				...this.devices[index],
				...updates
			};
		}
	}

	addOrUpdateDevice(device: Device) {
		const index = this.devices.findIndex((d) => d.id === device.id);
		if (index === -1) {
			this.devices = [...this.devices, device];
		} else {
			this.devices[index] = device;
		}
	}
}

export const deviceStore = new DeviceStore();
