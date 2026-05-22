import { apiFetch } from './client';
import type { Device, CreateDevicePayload, UpdateDevicePayload } from '$lib/types/device';

type FetchFn = typeof fetch;

export function listDevices(fetch: FetchFn, token: string) {
	return apiFetch<Device[]>(fetch, '/api/devices/devices/', { token });
}

export function getDevice(fetch: FetchFn, token: string, id: number) {
	return apiFetch<Device>(fetch, `/api/devices/devices/${id}/`, { token });
}

export function createDevice(fetch: FetchFn, token: string, body: CreateDevicePayload) {
	return apiFetch<Device>(fetch, '/api/devices/devices/', { method: 'POST', body, token });
}

export function updateDevice(
	fetch: FetchFn,
	token: string,
	id: number,
	body: UpdateDevicePayload
) {
	return apiFetch<Device>(fetch, `/api/devices/devices/${id}/`, {
		method: 'PATCH',
		body,
		token
	});
}

export function deleteDevice(fetch: FetchFn, token: string, id: number) {
	return apiFetch<null>(fetch, `/api/devices/devices/${id}/`, { method: 'DELETE', token });
}
