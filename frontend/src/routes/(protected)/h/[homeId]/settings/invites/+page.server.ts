import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { listHomeInvites, createHomeInvite, revokeHomeInvite } from '$lib/server/endpoints/invites';
import { ApiError } from '$lib/server/endpoints/client';

export const load: PageServerLoad = async ({ params, fetch, locals }) => {
	if (!locals.token) throw redirect(303, '/login');

	const homeId = Number(params.homeId);
	const invites = await listHomeInvites(fetch, locals.token, homeId);

	return { invites };
};

export const actions: Actions = {
	create: async ({ request, params, fetch, locals }) => {
		if (!locals.token) throw redirect(303, '/login');

		const data = await request.formData();
		const expiresInHoursRaw = String(data.get('expires_in_hours') ?? '24');
		const expiresInHours = Number(expiresInHoursRaw);

		if (!Number.isInteger(expiresInHours) || expiresInHours < 1 || expiresInHours > 720) {
			return fail(400, { error: 'Expiry must be between 1 and 720 hours' });
		}

		try {
			const invite = await createHomeInvite(fetch, locals.token, Number(params.homeId), {
				expires_in_hours: expiresInHours
			});
			return { success: true, invite };
		} catch (err) {
			if (err instanceof ApiError) {
				const body = err.body;
				let msg = err.message;
				if (body && typeof body === 'object') {
					if ('detail' in body) msg = String((body as { detail: unknown }).detail);
				}
				return fail(err.status, { error: msg });
			}
			throw err;
		}
	},

	revoke: async ({ request, params, fetch, locals }) => {
		if (!locals.token) throw redirect(303, '/login');

		const data = await request.formData();
		const inviteId = Number(data.get('id'));

		if (!Number.isInteger(inviteId) || inviteId <= 0) {
			return fail(400, { error: 'Invalid invite id' });
		}

		try {
			await revokeHomeInvite(fetch, locals.token, Number(params.homeId), inviteId);
			return { success: true, revoked: inviteId };
		} catch (err) {
			if (err instanceof ApiError) {
				const body = err.body;
				let msg = err.message;
				if (body && typeof body === 'object') {
					if ('detail' in body) msg = String((body as { detail: unknown }).detail);
				}
				return fail(err.status, { error: msg });
			}
			throw err;
		}
	}
};
