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
