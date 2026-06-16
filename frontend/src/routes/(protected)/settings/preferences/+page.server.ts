import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import {
	disableMfa,
	getMfaStatus,
	setupMfa,
	updateHomeMembership,
	verifyMfaSetup
} from '$lib/server/endpoints/users';
import { ApiError } from '$lib/server/endpoints/client';
import { canManageHome } from '$lib/server/permissions';

export const load: PageServerLoad = async ({ locals, fetch }) => {
	if (!locals.user || !locals.token) throw redirect(303, '/login');
	const homes = locals.homes ?? [];
	const manageableHomes = homes.filter((home) => canManageHome(home, locals.user!.id));

	const mfaStatus = await getMfaStatus(fetch, locals.token);

	return { manageableHomes, mfaStatus };
};

export const actions: Actions = {
	toggleDeviceManagement: async ({ request, locals, fetch }) => {
		if (!locals.token) throw redirect(303, '/login');

		const data = await request.formData();
		const membershipId = Number(data.get('membership_id'));
		const canManageDevices = data.get('can_manage_devices') === 'on';

		if (!Number.isInteger(membershipId) || membershipId <= 0) {
			return fail(400, { error: 'Invalid membership id', action: 'toggle', membershipId });
		}

		try {
			await updateHomeMembership(fetch, locals.token, membershipId, {
				can_manage_devices: canManageDevices
			});
			return { success: true, action: 'toggle', membershipId };
		} catch (err) {
			if (err instanceof ApiError) {
				const body = err.body;
				let msg = err.message;
				if (body && typeof body === 'object' && 'detail' in body) {
					msg = String((body as { detail: unknown }).detail);
				}
				return fail(err.status, { error: msg, action: 'toggle', membershipId });
			}
			throw err;
		}
	},

	setupMfa: async ({ locals, fetch }) => {
		if (!locals.token) throw redirect(303, '/login');

		try {
			const mfaSetup = await setupMfa(fetch, locals.token);
			return { mfaSetup };
		} catch (err) {
			if (err instanceof ApiError) {
				return fail(err.status, { error: 'Failed to start MFA setup' });
			}
			throw err;
		}
	},

	verifyMfa: async ({ request, locals, fetch }) => {
		if (!locals.token) throw redirect(303, '/login');

		const data = await request.formData();
		const code = String(data.get('code') ?? '');

		if (!code || code.length !== 6) {
			return fail(400, { error: 'Invalid code format', action: 'verifyMfa' });
		}

		try {
			await verifyMfaSetup(fetch, locals.token, code);
			return { success: true, action: 'verifyMfa' };
		} catch (err) {
			if (err instanceof ApiError) {
				let msg = 'Invalid MFA code';
				if (err.body && typeof err.body === 'object' && 'detail' in err.body) {
					msg = String((err.body as { detail: unknown }).detail);
				}
				return fail(err.status, { error: msg, action: 'verifyMfa' });
			}
			throw err;
		}
	},

	disableMfa: async ({ locals, fetch }) => {
		if (!locals.token) throw redirect(303, '/login');

		try {
			await disableMfa(fetch, locals.token);
			return { success: true, action: 'disableMfa' };
		} catch (err) {
			if (err instanceof ApiError) {
				return fail(err.status, { error: 'Failed to disable MFA' });
			}
			throw err;
		}
	}
};
