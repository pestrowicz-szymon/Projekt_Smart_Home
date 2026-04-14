import { redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ cookies, fetch }) => {
	const token = cookies.get('session');

	if (!token) {
		throw redirect(303, '/login');
	}

	const response = await fetch('http://127.0.0.1:8000/api/users/me/', {
		headers: {
			Authorization: `Bearer ${token}`
		}
	});

	if (response.status === 401 || response.status === 403) {
		cookies.delete('session', { path: '/' });
		throw redirect(303, '/login');
	}

	if (!response.ok) {
		return { user: null };
	}

	const user = await response.json();

	return { user };
};

export const actions: Actions = {
	logout: async ({ cookies }) => {
		cookies.delete('session', { path: '/' });
		throw redirect(303, '/login');
	}
};
