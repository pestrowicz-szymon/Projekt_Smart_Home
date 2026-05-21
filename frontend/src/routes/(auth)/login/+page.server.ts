import { fail, redirect } from '@sveltejs/kit';
import { ApiError } from '$lib/server/endpoints/client';
import { login } from '$lib/server/endpoints/auth';

export const actions = {
	default: async ({ request, cookies, fetch }) => {
		const data = await request.formData();
		const username = String(data.get('username') ?? '');
		const password = String(data.get('password') ?? '');

		try {
			const { access } = await login(fetch, { username, password });
			cookies.set('session', access, {
				httpOnly: true,
				sameSite: 'lax',
				path: '/',
				maxAge: 60 * 60 * 24
			});
			throw redirect(303, '/dashboard');
		} catch (err) {
			if (err instanceof ApiError) {
				return fail(err.status === 401 ? 401 : 500, { error: 'Invalid credentials' });
			}
			throw err;
		}
	}
};
