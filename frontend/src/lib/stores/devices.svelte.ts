import { browser } from '$app/environment';
import type { Device } from '$lib/types/device';

export type DeviceEvent =
	| {
			type: 'device_update';
			device_id: number;
			current_state: any;
			state_payload: any;
			last_seen_at: string;
			status: string;
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

	init(initialDevices: Device[]) {
		this.devices = initialDevices;
		const newHomeId = initialDevices[0]?.home_id ?? null;

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
			const index = this.devices.findIndex((d) => d.id === event.device_id);
			if (index !== -1) {
				this.devices[index] = {
					...this.devices[index],
					current_state: event.current_state,
					state_payload: event.state_payload,
					last_seen_at: event.last_seen_at,
					status: event.status as any
				};
			}
		} else if (event.type === 'action_acked' || event.type === 'action_failed') {
			// Optional: Handle action status updates specifically if needed
			// For now, device_update usually follows or is enough
			console.log(`Action ${event.type}:`, event.correlation_id);
		}
	}
}

export const deviceStore = new DeviceStore();
