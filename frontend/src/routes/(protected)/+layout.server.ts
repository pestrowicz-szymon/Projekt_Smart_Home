import { redirect } from '@sveltejs/kit';

export function load({ cookies }) {
	const token = cookies.get('session');
	if (!token) redirect(303, '/login');
	return {};
}
