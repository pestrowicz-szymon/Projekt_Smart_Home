import { apiFetch } from './client';
import { createLogger } from '../logger';
import type { LoginResponse, RegisterPayload, User } from '$lib/types/auth';

type FetchFn = typeof fetch;
const log = createLogger('auth-endpoint');

export function login(fetch: FetchFn, body: { username: string; password: string }) {
	log.debug({ username: body.username }, 'Attempting login');
	return apiFetch<LoginResponse>(fetch, '/api/users/login/', { method: 'POST', body });
}

export function loginMfa(fetch: FetchFn, body: { mfa_token: string; mfa_code: string }) {
	log.debug({ mfa_token: body.mfa_token }, 'Attempting MFA login');
	return apiFetch<LoginResponse>(fetch, '/api/users/login/', { method: 'POST', body });
}

export function register(fetch: FetchFn, body: RegisterPayload) {
	log.debug({ username: body.username }, 'Attempting registration');
	return apiFetch<{ message: string }>(fetch, '/api/users/register/', { method: 'POST', body });
}

export function me(fetch: FetchFn, token: string) {
	log.debug('Fetching current user profile');
	return apiFetch<User>(fetch, '/api/users/me/', { token });
}

export function logout(fetch: FetchFn, token: string) {
	log.debug('Logging out');
	return apiFetch<{ message: string }>(fetch, '/api/users/logout/', { method: 'POST', token });
}

export function refreshAccessToken(fetch: FetchFn, refresh: string) {
	log.debug('Refreshing access token');
	return apiFetch<{ access: string; refresh?: string }>(fetch, '/api/token/refresh/', {
		method: 'POST',
		body: { refresh }
	});
}
