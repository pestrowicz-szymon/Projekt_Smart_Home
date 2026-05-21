import { redirect } from '@sveltejs/kit';

export async function load({ cookies }) {
	if (cookies.get('session')) {
		throw redirect(303, '/dashboard');
	}
	return {};
}
