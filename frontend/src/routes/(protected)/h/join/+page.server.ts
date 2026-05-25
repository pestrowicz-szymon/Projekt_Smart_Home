import { redirect, fail } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { redeemInvite } from '$lib/server/endpoints/invites';
import { ApiError } from '$lib/server/endpoints/client';

export const load: PageServerLoad = ({ locals }) => {
	if (!locals.user) throw redirect(303, '/login');
	return { user: locals.user, token: locals.token };
};

export const actions: Actions = {
	redeem: async ({ request, fetch, locals }) => {
		if (!locals.token) throw redirect(303, '/login');

		const data = await request.formData();
		const code = String(data.get('code') ?? '').trim();

		if (!code) return fail(400, { error: 'Invite code is required' });
		if (code.length < 8) return fail(400, { error: 'Invalid invite code format' });

		try {
			const member = await redeemInvite(fetch, locals.token, { code }); // Redirect to the home they were added to
			throw redirect(303, `/h/${member.home}`);
		} catch (err) {
			if (err instanceof ApiError) {
				const body = err.body;
				let msg = err.message;
				if (body && typeof body === 'object') {
					if ('detail' in body) msg = String((body as { detail: unknown }).detail);
					else if ('code' in body) msg = 'Invalid or expired invite code';
				}
				return fail(err.status, { error: msg, values: { code } });
			}
			if (err instanceof Response) throw err; // Re-throw redirects
			throw err;
		}
	}
};
