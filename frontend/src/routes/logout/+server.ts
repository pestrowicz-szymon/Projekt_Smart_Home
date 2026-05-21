import { redirect } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { logout } from '$lib/server/endpoints/auth';

export const POST: RequestHandler = async ({ cookies, fetch }) => {
	const token = cookies.get('session');
	if (token) {
		try {
			await logout(fetch, token);
		} catch {
			// non-fatal: clear the cookie below regardless
		}
	}
	cookies.delete('session', { path: '/' });
	cookies.delete('activeHomeId', { path: '/' });
	throw redirect(303, '/login');
};
