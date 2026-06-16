import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { updateHomeMembership } from '$lib/server/endpoints/users';
import { ApiError } from '$lib/server/endpoints/client';
import { canManageHome } from '$lib/server/permissions';

export const load: PageServerLoad = ({ locals }) => {
	if (!locals.user) throw redirect(303, '/login');
	const homes = locals.homes ?? [];
	const manageableHomes = homes.filter((home) => canManageHome(home, locals.user!.id));
	return { manageableHomes };
};

export const actions: Actions = {
	toggleDeviceManagement: async ({ request, locals, fetch }) => {
		if (!locals.token) throw redirect(303, '/login');

		const data = await request.formData();
		const membershipId = Number(data.get('membership_id'));
		const canManageDevices = data.get('can_manage_devices') === 'on';

		if (!Number.isInteger(membershipId) || membershipId <= 0) {
			return fail(400, { error: 'Invalid membership id', action: 'toggle', membershipId });
		}

		try {
			await updateHomeMembership(fetch, locals.token, membershipId, {
				can_manage_devices: canManageDevices
			});
			return { success: true, action: 'toggle', membershipId };
		} catch (err) {
			if (err instanceof ApiError) {
				const body = err.body;
				let msg = err.message;
				if (body && typeof body === 'object' && 'detail' in body) {
					msg = String((body as { detail: unknown }).detail);
				}
				return fail(err.status, { error: msg, action: 'toggle', membershipId });
			}
			throw err;
		}
	}
};
