import type { Home } from './home';

export type DeviceType =
	| 'thermometer'
	| 'lock'
	| 'light'
	| 'smoke_detector'
	| 'generic_sensor'
	| 'actuator';

export type DeviceStatus = 'unknown' | 'online' | 'offline';

export interface Room {
	id: number;
	home: number;
	name: string;
	description: string;
	created_at: string;
	updated_at: string;
	devices?: Device[];
}

export interface CreateRoomPayload {
	home: number;
	name: string;
	description?: string;
}

export interface UpdateRoomPayload {
	name?: string;
	description?: string;
}

export interface Device {
	id: number;
	home: Home;
	room?: Room | null;
	room_id?: number | null;
	name: string;
	device_type: DeviceType;
	hardware_id: string;
	status: DeviceStatus;
	is_active: boolean;
	current_state: number;
	state_payload: Record<string, unknown>;
	certificate_fingerprint: string | null;
	last_seen_at: string | null;
	created_at: string;
	updated_at: string;
}

export interface CreateDevicePayload {
	home_id: number;
	room_id?: number | null;
	name: string;
	device_type: DeviceType;
	hardware_id: string;
	is_active?: boolean;
}

export interface UpdateDevicePayload {
	room_id?: number | null;
	name?: string;
	device_type?: DeviceType;
	hardware_id?: string;
	is_active?: boolean;
}

export const DEVICE_TYPE_LABEL: Record<DeviceType, string> = {
	thermometer: 'Thermometer',
	lock: 'Lock',
	light: 'Light',
	smoke_detector: 'Smoke detector',
	generic_sensor: 'Sensor',
	actuator: 'Actuator'
};

export const DEVICE_TYPES: DeviceType[] = [
	'thermometer',
	'lock',
	'light',
	'smoke_detector',
	'generic_sensor',
	'actuator'
];
