import { fail, redirect } from '@sveltejs/kit';
import type { Actions } from './$types';
import { deleteHome } from '$lib/server/endpoints/homes';
import { ApiError } from '$lib/server/endpoints/client';

export const actions: Actions = {
	delete: async ({ request, params, fetch, locals }) => {
		if (!locals.token) throw redirect(303, '/login');

		const data = await request.formData();
		const confirmation = String(data.get('confirmation') ?? '').trim();
		const expected = String(data.get('expected') ?? '').trim();

		if (!expected || confirmation !== expected) {
			return fail(400, { error: 'Type the home name exactly to confirm.' });
		}

		try {
			await deleteHome(fetch, locals.token, Number(params.homeId));
		} catch (err) {
			if (err instanceof ApiError) {
				return fail(err.status, { error: err.message });
			}
			throw err;
		}

		throw redirect(303, '/h');
	}
};
