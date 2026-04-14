// src/routes/login/+page.server.ts
import { redirect, fail } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = () => {
	return {};
};

export const actions: Actions = {
	default: async ({ request, cookies, fetch }) => {
		const data = await request.formData();
		const res = await fetch('http://127.0.0.1:8000/api/users/login/', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				username: data.get('username'),
				password: data.get('password')
			})
		});

		if (!res.ok) return fail(401, { error: 'Invalid credentials' });

		const payload = await res.json();
		const token = payload.access ?? payload.token;

		if (!token || typeof token !== 'string') {
			return fail(500, { error: 'Login succeeded but token is missing in response' });
		}

		cookies.set('session', token, {
			httpOnly: true,
			sameSite: 'strict',
			path: '/',
			maxAge: 60 * 60 * 24 // 1 day
		});

		throw redirect(303, '/');
	}
};
