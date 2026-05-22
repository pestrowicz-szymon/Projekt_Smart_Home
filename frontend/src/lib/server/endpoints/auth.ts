import { apiFetch } from './client';
import type { LoginResponse, RegisterPayload, User } from '$lib/types/auth';

type FetchFn = typeof fetch;

export function login(fetch: FetchFn, body: { username: string; password: string }) {
	return apiFetch<LoginResponse>(fetch, '/api/users/login/', { method: 'POST', body });
}

export function register(fetch: FetchFn, body: RegisterPayload) {
	return apiFetch<{ message: string }>(fetch, '/api/users/register/', { method: 'POST', body });
}

export function me(fetch: FetchFn, token: string) {
	return apiFetch<User>(fetch, '/api/users/me/', { token });
}

export function logout(fetch: FetchFn, token: string) {
	return apiFetch<{ message: string }>(fetch, '/api/users/logout/', { method: 'POST', token });
}

export function refreshAccessToken(fetch: FetchFn, refresh: string) {
	return apiFetch<{ access: string; refresh?: string }>(fetch, '/api/token/refresh/', {
		method: 'POST',
		body: { refresh }
	});
}
