import type { PageServerLoad } from './$types';

export const load: PageServerLoad = ({ locals }) => {
	return {
		homes: locals.homes ?? [],
		activeHomeId: locals.activeHome?.id ?? null,
		currentUserId: locals.user?.id ?? null
	};
};
