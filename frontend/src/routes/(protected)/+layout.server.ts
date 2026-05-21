import { redirect } from '@sveltejs/kit';
import { ApiError } from '$lib/server/endpoints/client';
import { me } from '$lib/server/endpoints/auth';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ cookies, fetch }) => {
	const token = cookies.get('session');
	if (!token) throw redirect(303, '/login');

	try {
		const user = await me(fetch, token);
		return { user };
	} catch (err) {
		if (err instanceof ApiError && (err.status === 401 || err.status === 403)) {
			cookies.delete('session', { path: '/' });
			throw redirect(303, '/login');
		}
		throw err;
	}
};
