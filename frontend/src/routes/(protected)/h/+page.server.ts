import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = ({ locals }) => {
	if (!locals.activeHome) throw redirect(303, '/onboarding');
	throw redirect(303, `/h/${locals.activeHome.id}/dashboard`);
};
