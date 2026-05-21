import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { createHome } from '$lib/server/endpoints/homes';
import { ApiError } from '$lib/server/endpoints/client';

export const load: PageServerLoad = ({ locals }) => {
	if ((locals.homes?.length ?? 0) > 0) {
		throw redirect(303, '/h');
	}
	return {};
};

export const actions: Actions = {
	default: async ({ request, fetch, locals, cookies }) => {
		if (!locals.token) throw redirect(303, '/login');
		const data = await request.formData();
		const name = String(data.get('name') ?? '').trim();
		if (!name) return fail(400, { error: 'Name is required' });

		try {
			const home = await createHome(fetch, locals.token, {
				name,
				description: String(data.get('description') ?? '')
			});
			cookies.set('activeHomeId', String(home.id), {
				path: '/',
				httpOnly: true,
				sameSite: 'lax'
			});
			throw redirect(303, `/h/${home.id}/dashboard`);
		} catch (err) {
			if (err instanceof ApiError) return fail(err.status, { error: err.message });
			throw err;
		}
	}
};
