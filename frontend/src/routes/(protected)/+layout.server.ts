import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = ({ locals, cookies }) => {
	if (!locals.user) throw redirect(303, '/login');

	const activeHome = locals.activeHome;
	if (activeHome) {
		const cookieId = cookies.get('activeHomeId');
		if (cookieId !== String(activeHome.id)) {
			cookies.set('activeHomeId', String(activeHome.id), {
				path: '/',
				httpOnly: true,
				sameSite: 'lax'
			});
		}
	}

	return {
		user: locals.user,
		homes: locals.homes ?? [],
		activeHome: activeHome ?? null
	};
};
