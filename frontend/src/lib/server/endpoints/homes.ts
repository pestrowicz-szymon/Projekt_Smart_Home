import { apiFetch } from './client';
import type {
	Home,
	HomeMember,
	CreateHomePayload,
	UpdateHomePayload,
	HomeRole
} from '$lib/types/home';

type FetchFn = typeof fetch;

export function listHomes(fetch: FetchFn, token: string) {
	return apiFetch<Home[]>(fetch, '/api/devices/homes/', { token });
}

export function createHome(fetch: FetchFn, token: string, body: CreateHomePayload) {
	return apiFetch<Home>(fetch, '/api/devices/homes/', { method: 'POST', body, token });
}

export function updateHome(fetch: FetchFn, token: string, id: number, body: UpdateHomePayload) {
	return apiFetch<Home>(fetch, `/api/devices/homes/${id}/`, { method: 'PATCH', body, token });
}

export function deleteHome(fetch: FetchFn, token: string, id: number) {
	return apiFetch<null>(fetch, `/api/devices/homes/${id}/`, { method: 'DELETE', token });
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
