import { apiFetch } from './client';
import { createLogger } from '../logger';
import type { Device, CreateDevicePayload, UpdateDevicePayload } from '$lib/types/device';

type FetchFn = typeof fetch;
const log = createLogger('devices-endpoint');

export function listDevices(fetch: FetchFn, token: string) {
	log.debug('Fetching list of devices');
	return apiFetch<Device[]>(fetch, '/api/devices/devices/', { token });
}

export function getDevice(fetch: FetchFn, token: string, id: number) {
	log.debug({ id }, `Fetching device ${id}`);
	return apiFetch<Device>(fetch, `/api/devices/devices/${id}/`, { token });
}

export function createDevice(fetch: FetchFn, token: string, body: CreateDevicePayload) {
	log.debug({ body }, 'Creating new device');
	return apiFetch<Device>(fetch, '/api/devices/devices/', { method: 'POST', body, token });
}

export function updateDevice(fetch: FetchFn, token: string, id: number, body: UpdateDevicePayload) {
	log.debug({ id, body }, `Updating device ${id}`);
	return apiFetch<Device>(fetch, `/api/devices/devices/${id}/`, {
		method: 'PATCH',
		body,
		token
	});
}

export function deleteDevice(fetch: FetchFn, token: string, id: number) {
	log.debug({ id }, `Deleting device ${id}`);
	return apiFetch<null>(fetch, `/api/devices/devices/${id}/`, { method: 'DELETE', token });
}

export function sendDeviceAction(
	fetch: FetchFn,
	token: string,
	id: number,
	action_type: string,
	payload: Record<string, unknown> = {}
) {
	log.debug({ id, action_type, payload }, `Sending action to device ${id}`);
	return apiFetch(fetch, `/api/devices/devices/${id}/actions/`, {
		method: 'POST',
		body: { action_type, payload },
		token
	});
}
