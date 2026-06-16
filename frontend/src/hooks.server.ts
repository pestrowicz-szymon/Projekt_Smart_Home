import type { Cookies, Handle } from '@sveltejs/kit';
import { ApiError } from '$lib/server/endpoints/client';
import { me, refreshAccessToken } from '$lib/server/endpoints/auth';
import { listHomes } from '$lib/server/endpoints/homes';

const ACCESS_MAX_AGE = 60 * 60;
const REFRESH_MAX_AGE = 60 * 60 * 24;

function setAccessCookie(cookies: Cookies, access: string) {
	cookies.set('session', access, {
		httpOnly: true,
		sameSite: 'lax',
		path: '/',
		maxAge: ACCESS_MAX_AGE
	});
}

function setRefreshCookie(cookies: Cookies, refresh: string) {
	cookies.set('refresh', refresh, {
		httpOnly: true,
		sameSite: 'lax',
		path: '/',
		maxAge: REFRESH_MAX_AGE
	});
}

function clearAuth(cookies: Cookies) {
	cookies.delete('session', { path: '/' });
	cookies.delete('refresh', { path: '/' });
}

async function tryRefresh(
	fetch: typeof globalThis.fetch,
	cookies: Cookies
): Promise<string | null> {
	const refresh = cookies.get('refresh');
	if (!refresh) return null;

	try {
		const result = await refreshAccessToken(fetch, refresh);
		setAccessCookie(cookies, result.access);
		if (result.refresh) setRefreshCookie(cookies, result.refresh);
		return result.access;
	} catch {
		clearAuth(cookies);
		return null;
	}
}

export const handle: Handle = async ({ event, resolve }) => {
	let token = event.cookies.get('session');

	if (!token && event.cookies.get('refresh')) {
		token = (await tryRefresh(event.fetch, event.cookies)) ?? undefined;
	}

	if (!token) return resolve(event);

	const loadSession = async (accessToken: string) => {
		const [user, homes] = await Promise.all([
			me(event.fetch, accessToken),
			listHomes(event.fetch, accessToken)
		]);
		event.locals.user = user;
		event.locals.token = accessToken;
		event.locals.homes = homes;

		const cookieId = Number(event.cookies.get('activeHomeId'));
		event.locals.activeHome = homes.find((h) => h.id === cookieId) ?? homes[0] ?? null;
	};

	try {
		await loadSession(token);
	} catch (err) {
		if (!(err instanceof ApiError) || (err.status !== 401 && err.status !== 403)) {
			throw err;
		}
		const refreshed = await tryRefresh(event.fetch, event.cookies);
		if (!refreshed) {
			clearAuth(event.cookies);
			return resolve(event);
		}
		try {
			await loadSession(refreshed);
		} catch (retryErr) {
			if (retryErr instanceof ApiError && (retryErr.status === 401 || retryErr.status === 403)) {
				clearAuth(event.cookies);
				return resolve(event);
			}
			throw retryErr;
		}
	}

	return resolve(event);
};
