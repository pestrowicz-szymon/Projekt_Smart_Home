import { apiFetch } from './client';

export interface User {
	id: number;
	username: string;
	email: string;
	first_name: string;
	last_name: string;
}

export interface LoginResponse {
	access: string;
	refresh: string;
	user?: User;
}

export interface RegisterPayload {
	username: string;
	email: string;
	password: string;
	password2: string;
	first_name: string;
	last_name: string;
}

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
