import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { ApiError } from '$lib/server/endpoints/client';
import { loginMfa } from '$lib/server/endpoints/auth';

const ACCESS_MAX_AGE = 60 * 60;
const REFRESH_MAX_AGE = 60 * 60 * 24;

export const load: PageServerLoad = async ({ url }) => {
	const mfaToken = url.searchParams.get('mfa_token');
	if (!mfaToken) {
		throw redirect(303, '/login');
	}
	return { mfaToken };
};

export const actions: Actions = {
	default: async ({ request, cookies, fetch, url }) => {
		const mfaToken = url.searchParams.get('mfa_token');
		if (!mfaToken) {
			throw redirect(303, '/login');
		}

		const data = await request.formData();
		const mfaCode = String(data.get('mfa_code') ?? '');

		if (!mfaCode || mfaCode.length !== 6) {
			return fail(400, { error: 'Invalid MFA code' });
		}

		try {
			const { access, refresh } = await loginMfa(fetch, {
				mfa_token: mfaToken,
				mfa_code: mfaCode
			});

			if (!access || !refresh) {
				return fail(500, { error: 'Authentication failed: missing tokens' });
			}

			cookies.set('session', access, {
				httpOnly: true,
				sameSite: 'lax',
				path: '/',
				maxAge: ACCESS_MAX_AGE,
				secure: process.env.NODE_ENV === 'production'
			});
			cookies.set('refresh', refresh, {
				httpOnly: true,
				sameSite: 'lax',
				path: '/',
				maxAge: REFRESH_MAX_AGE,
				secure: process.env.NODE_ENV === 'production'
			});
			throw redirect(303, '/h');
		} catch (err) {
			if (err instanceof ApiError) {
				let msg = 'Invalid MFA code';
				if (err.body && typeof err.body === 'object' && 'detail' in err.body) {
					msg = String((err.body as { detail: unknown }).detail);
				}
				return fail(err.status, { error: msg });
			}
			throw err;
		}
	}
};
