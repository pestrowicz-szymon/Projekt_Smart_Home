import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import {
	disableMfa,
	getMfaStatus,
	setupMfa,
	verifyMfaSetup
} from '$lib/server/endpoints/users';
import { ApiError } from '$lib/server/endpoints/client';

export const load: PageServerLoad = async ({ locals, fetch }) => {
	if (!locals.user || !locals.token) throw redirect(303, '/login');

	const mfaStatus = await getMfaStatus(fetch, locals.token);

	return { mfaStatus };
};

export const actions: Actions = {
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
