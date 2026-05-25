import { apiFetch } from './client';
import { createLogger } from '../logger';
import type {
	Home,
	HomeMember,
	CreateHomePayload,
	UpdateHomePayload,
	HomeRole
} from '$lib/types/home';
import type { Device } from '$lib/types/device';

type FetchFn = typeof fetch;
const log = createLogger('homes-endpoint');

export function listHomes(fetch: FetchFn, token: string) {
	log.debug('Fetching list of homes');
	return apiFetch<Home[]>(fetch, '/api/devices/homes/', { token });
}

export function listHomeDevices(fetch: FetchFn, token: string, homeId: number) {
	log.debug({ homeId }, `Fetching devices for home ${homeId}`);
	return apiFetch<Device[]>(fetch, `/api/devices/homes/${homeId}/devices/`, { token });
}

export function createHome(fetch: FetchFn, token: string, body: CreateHomePayload) {
	log.debug({ body }, 'Creating new home');
	return apiFetch<Home>(fetch, '/api/devices/homes/', { method: 'POST', body, token });
}

export function updateHome(fetch: FetchFn, token: string, id: number, body: UpdateHomePayload) {
	log.debug({ id, body }, `Updating home ${id}`);
	return apiFetch<Home>(fetch, `/api/devices/homes/${id}/`, { method: 'PATCH', body, token });
}

export function deleteHome(fetch: FetchFn, token: string, id: number) {
	log.debug({ id }, `Deleting home ${id}`);
	return apiFetch<null>(fetch, `/api/devices/homes/${id}/`, { method: 'DELETE', token });
}

export function listMembers(fetch: FetchFn, token: string, homeId: number) {
	log.debug({ homeId }, `Fetching members for home ${homeId}`);
	return apiFetch<HomeMember[]>(fetch, `/api/devices/homes/${homeId}/members/`, { token });
}

export function addMember(
	fetch: FetchFn,
	token: string,
	homeId: number,
	body: { user_id: number; role: HomeRole; can_manage_devices?: boolean }
) {
	log.debug({ homeId, body }, `Adding member to home ${homeId}`);
	return apiFetch<HomeMember>(fetch, `/api/devices/homes/${homeId}/members/`, {
		method: 'POST',
		body,
		token
	});
}
