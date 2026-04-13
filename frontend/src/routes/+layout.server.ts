import { redirect } from '@sveltejs/kit';

export function load({ cookies, url }) {
	if (url.pathname.startsWith('/login') || url.pathname.startsWith('/register')) {
		return {};
	}

	const token = cookies.get('session');
	if (!token) throw redirect(303, '/login');

	return {};
}
