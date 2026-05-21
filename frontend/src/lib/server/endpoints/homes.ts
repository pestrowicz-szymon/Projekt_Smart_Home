import { apiFetch } from './client';
import type { Home, HomeMember, CreateHomePayload, HomeRole } from '$lib/types/home';

type FetchFn = typeof fetch;

export function listHomes(fetch: FetchFn, token: string) {
	return apiFetch<Home[]>(fetch, '/api/devices/homes/', { token });
}

export function createHome(fetch: FetchFn, token: string, body: CreateHomePayload) {
	return apiFetch<Home>(fetch, '/api/devices/homes/', { method: 'POST', body, token });
}

export function listMembers(fetch: FetchFn, token: string, homeId: number) {
	return apiFetch<HomeMember[]>(fetch, `/api/devices/homes/${homeId}/members/`, { token });
}

export function addMember(
	fetch: FetchFn,
	token: string,
	homeId: number,
	body: { user_id: number; role: HomeRole; can_manage_devices?: boolean }
) {
	return apiFetch<HomeMember>(fetch, `/api/devices/homes/${homeId}/members/`, {
		method: 'POST',
		body,
		token
	});
}
