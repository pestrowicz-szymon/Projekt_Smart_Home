// src/routes/login/+page.server.ts
import { redirect, fail } from '@sveltejs/kit';

export const actions = {
	default: async ({ request, cookies, fetch }) => {
		const data = await request.formData();
		const res = await fetch('http://backend/api/auth/login', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				username: data.get('username'),
				password: data.get('password')
			})
		});

		if (!res.ok) return fail(401, { error: 'Invalid credentials' });

		const { token } = await res.json();
		cookies.set('session', token, {
			httpOnly: true,
			sameSite: 'strict',
			path: '/',
			maxAge: 60 * 60 * 24 // 1 day
		});

		redirect(303, '/');
	}
};
