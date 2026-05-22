import { error } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = ({ params, locals, cookies }) => {
	const id = Number(params.homeId);
	const home = locals.homes?.find((h) => h.id === id);
	if (!home) throw error(404, 'Home not found');

	if (locals.activeHome?.id !== id) {
		cookies.set('activeHomeId', String(id), {
			path: '/',
			httpOnly: true,
			sameSite: 'lax'
		});
	}
	return { home };
};
