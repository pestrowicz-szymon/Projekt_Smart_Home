import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { createHome } from '$lib/server/endpoints/homes';
import { ApiError } from '$lib/server/endpoints/client';

export const load: PageServerLoad = () => {
	return {};
};

export const actions: Actions = {
	default: async ({ request, fetch, locals, cookies }) => {
		if (!locals.token) throw redirect(303, '/login');

		const data = await request.formData();
		const name = String(data.get('name') ?? '').trim();
		const description = String(data.get('description') ?? '').trim();

		if (!name) {
			return fail(400, { error: 'Name is required', values: { name, description } });
		}

		let homeId: number;
		try {
			const home = await createHome(fetch, locals.token, { name, description });
			homeId = home.id;
		} catch (err) {
			if (err instanceof ApiError) {
				return fail(err.status, { error: err.message, values: { name, description } });
			}
			throw err;
		}

		cookies.set('activeHomeId', String(homeId), {
			path: '/',
			httpOnly: true,
			sameSite: 'lax'
		});
		throw redirect(303, `/h/${homeId}/dashboard`);
	}
};
