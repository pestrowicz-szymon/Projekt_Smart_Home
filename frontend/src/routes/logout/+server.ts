import { redirect } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { logout } from '$lib/server/endpoints/auth';

export const POST: RequestHandler = async ({ cookies, fetch }) => {
	const token = cookies.get('session');
	const refresh = cookies.get('refresh');
	if (token && refresh) {
		try {
			await logout(fetch, token, refresh);
		} catch {
			// non-fatal: clear the cookie below regardless
		}
	}
	cookies.delete('session', { path: '/' });
	cookies.delete('refresh', { path: '/' });
	cookies.delete('activeHomeId', { path: '/' });
	throw redirect(303, '/login');
};
