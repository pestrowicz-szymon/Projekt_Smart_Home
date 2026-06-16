import { apiFetch } from './client';
import { createLogger } from '../logger';
import type { HomeMembership } from '$lib/types/auth';

type FetchFn = typeof fetch;
const log = createLogger('users-endpoint');

export function updateHomeMembership(
	fetch: FetchFn,
	token: string,
	membershipId: number,
	body: { can_manage_devices: boolean }
) {
	log.debug({ membershipId, body }, `Updating membership ${membershipId}`);
	return apiFetch<HomeMembership>(fetch, `/api/users/memberships/${membershipId}/`, {
		method: 'PATCH',
		body,
		token
	});
}

export function getMfaStatus(fetch: FetchFn, token: string) {
	log.debug('Fetching MFA status');
	return apiFetch<{ enabled: boolean }>(fetch, '/api/users/mfa/status/', { token });
}

export function setupMfa(fetch: FetchFn, token: string) {
	log.debug('Setting up MFA');
	return apiFetch<{ mfa_enabled: boolean; secret: string; otpauth_uri: string }>(
		fetch,
		'/api/users/mfa/setup/',
		{ method: 'POST', token }
	);
}

export function verifyMfaSetup(fetch: FetchFn, token: string, code: string) {
	log.debug({ code }, 'Verifying MFA setup');
	return apiFetch<{ enabled: boolean }>(fetch, '/api/users/mfa/verify/', {
		method: 'POST',
		body: { code },
		token
	});
}

export function disableMfa(fetch: FetchFn, token: string) {
	log.debug('Disabling MFA');
	return apiFetch<{ detail: string }>(fetch, '/api/users/mfa/disable/', {
		method: 'POST',
		token
	});
}
