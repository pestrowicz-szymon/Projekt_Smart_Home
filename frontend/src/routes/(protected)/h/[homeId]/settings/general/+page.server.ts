import { fail, redirect } from '@sveltejs/kit';
import type { Actions } from './$types';
import { updateHome } from '$lib/server/endpoints/homes';
import { ApiError } from '$lib/server/endpoints/client';

export const actions: Actions = {
	default: async ({ request, params, fetch, locals }) => {
		if (!locals.token) throw redirect(303, '/login');

		const data = await request.formData();
		const name = String(data.get('name') ?? '').trim();
		const description = String(data.get('description') ?? '').trim();

		if (!name) {
			return fail(400, { error: 'Name is required', values: { name, description } });
		}

		try {
			await updateHome(fetch, locals.token, Number(params.homeId), { name, description });
			return { success: true };
		} catch (err) {
			if (err instanceof ApiError) {
				return fail(err.status, { error: err.message, values: { name, description } });
			}
			throw err;
		}
	}
};
