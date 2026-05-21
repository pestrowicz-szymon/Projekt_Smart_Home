import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = ({ locals }) => {
	if ((locals.homes?.length ?? 0) > 0) {
		throw redirect(303, '/h');
	}
	return { user: locals.user };
};
