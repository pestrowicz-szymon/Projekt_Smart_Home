import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = ({ locals, url }) => {
	if (!locals.user) throw redirect(303, '/login');

	const hasHomes = (locals.homes?.length ?? 0) > 0;
	if (!hasHomes && url.pathname !== '/onboarding') {
		throw redirect(303, '/onboarding');
	}

	return {
		user: locals.user,
		homes: locals.homes ?? [],
		activeHome: locals.activeHome ?? null
	};
};
