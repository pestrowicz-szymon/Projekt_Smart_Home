import type { Handle } from '@sveltejs/kit';
import { ApiError } from '$lib/server/endpoints/client';
import { me } from '$lib/server/endpoints/auth';
import { listHomes } from '$lib/server/endpoints/homes';

export const handle: Handle = async ({ event, resolve }) => {
	const token = event.cookies.get('session');
	if (!token) return resolve(event);

	try {
		const [user, homes] = await Promise.all([
			me(event.fetch, token),
			listHomes(event.fetch, token)
		]);
		event.locals.user = user;
		event.locals.token = token;

		const cookieId = Number(event.cookies.get('activeHomeId'));
		event.locals.activeHome = homes.find((h) => h.id === cookieId) ?? homes[0] ?? null;
	} catch (err) {
		if (err instanceof ApiError && (err.status === 401 || err.status === 403)) {
			event.cookies.delete('session', { path: '/' });
		} else {
			throw err;
		}
	}

	return resolve(event);
};
