import { apiFetch } from './client';
import { createLogger } from '../logger';

type FetchFn = typeof fetch;
const log = createLogger('invites-endpoint');

export interface HomeInvite {
	id: number;
	home: number;
	created_by: {
		id: number;
		first_name: string;
		last_name: string;
	};
	code?: string;
	expires_at: string;
	used_by: null | {
		id: number;
		first_name: string;
		last_name: string;
	};
	used_at: string | null;
	revoked_at: string | null;
	status: 'active' | 'used' | 'revoked' | 'expired';
	created_at: string;
	updated_at: string;
}

export interface CreateInvitePayload {
	expires_in_hours?: number;
}

export interface RedeemInvitePayload {
	code: string;
}

export interface HomeMember {
	id: number;
	home: number;
	user: {
		id: number;
		first_name: string;
		last_name: string;
	};
	role: string;
	can_manage_devices: boolean;
	created_at: string;
}

export function listHomeInvites(fetch: FetchFn, token: string, homeId: number) {
	log.debug({ homeId }, `Fetching invites for home ${homeId}`);
	return apiFetch<HomeInvite[]>(fetch, `/api/invites/homes/${homeId}/invites/`, { token });
}

export function createHomeInvite(
	fetch: FetchFn,
	token: string,
	homeId: number,
	body?: CreateInvitePayload
) {
	log.debug({ homeId, body }, `Creating invite for home ${homeId}`);
	return apiFetch<HomeInvite>(fetch, `/api/invites/homes/${homeId}/invites/`, {
		method: 'POST',
		body,
		token
	});
}

export function revokeHomeInvite(fetch: FetchFn, token: string, homeId: number, inviteId: number) {
	log.debug({ homeId, inviteId }, `Revoking invite ${inviteId} for home ${homeId}`);
	return apiFetch<HomeInvite>(fetch, `/api/invites/homes/${homeId}/invites/${inviteId}/`, {
		method: 'DELETE',
		token
	});
}

export function redeemInvite(fetch: FetchFn, body: RedeemInvitePayload) {
	log.debug({ code: body.code.substring(0, 8) + '...' }, 'Redeeming invite');
	return apiFetch<HomeMember>(fetch, '/api/invites/redeem/', { method: 'POST', body });
}
