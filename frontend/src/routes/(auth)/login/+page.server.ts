import { fail, redirect } from '@sveltejs/kit';
import { ApiError } from '$lib/server/endpoints/client';
import { login } from '$lib/server/endpoints/auth';

const ACCESS_MAX_AGE = 60 * 60;
const REFRESH_MAX_AGE = 60 * 60 * 24;

export const actions = {
	default: async ({ request, cookies, fetch }) => {
		const data = await request.formData();
		const username = String(data.get('username') ?? '');
		const password = String(data.get('password') ?? '');

		try {
			const res = await login(fetch, { username, password });

			if (res.mfa_required) {
				const params = new URLSearchParams({
					mfa_token: res.mfa_token ?? '',
					expires_at: res.expires_at ?? ''
				});
				throw redirect(303, `/login/mfa?${params.toString()}`);
			}

			const { access, refresh } = res;
			if (!access || !refresh) {
				return fail(500, { error: 'Authentication failed: missing tokens' });
			}

			cookies.set('session', access, {
				httpOnly: true,
				sameSite: 'lax',
				path: '/',
				maxAge: ACCESS_MAX_AGE
			});
			cookies.set('refresh', refresh, {
				httpOnly: true,
				sameSite: 'lax',
				path: '/',
				maxAge: REFRESH_MAX_AGE
			});
			throw redirect(303, '/h');
		} catch (err) {
			if (err instanceof ApiError) {
				return fail(err.status === 401 ? 401 : 500, { error: 'Invalid credentials' });
			}
			throw err;
		}
	}
};
