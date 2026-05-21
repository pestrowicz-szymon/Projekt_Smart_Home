import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { addMember } from '$lib/server/endpoints/homes';
import { ApiError } from '$lib/server/endpoints/client';
import type { Home, HomeRole } from '$lib/types/home';

const ROLES: HomeRole[] = ['admin', 'member', 'viewer'];

function canManageMembers(home: Home, userId: number): boolean {
	if (home.owner.id === userId) return true;
	const m = home.members.find((m) => m.user.id === userId);
	if (!m) return false;
	return m.role === 'owner' || m.role === 'admin' || m.can_manage_devices;
}

export const load: PageServerLoad = async ({ parent, locals }) => {
	const { home } = await parent();
	return {
		canManage: canManageMembers(home, locals.user!.id)
	};
};

export const actions: Actions = {
	default: async ({ request, params, fetch, locals }) => {
		if (!locals.token) throw redirect(303, '/login');

		const data = await request.formData();
		const userIdRaw = String(data.get('user_id') ?? '').trim();
		const roleRaw = String(data.get('role') ?? 'member');
		const canManageDevices = data.get('can_manage_devices') === 'on';

		const userId = Number(userIdRaw);
		if (!userIdRaw || !Number.isInteger(userId) || userId <= 0) {
			return fail(400, { error: 'Valid user ID is required' });
		}
		if (!ROLES.includes(roleRaw as HomeRole)) {
			return fail(400, { error: 'Invalid role' });
		}

		try {
			await addMember(fetch, locals.token, Number(params.homeId), {
				user_id: userId,
				role: roleRaw as HomeRole,
				can_manage_devices: canManageDevices
			});
			return { success: true };
		} catch (err) {
			if (err instanceof ApiError) {
				const msg =
					typeof err.body === 'object' && err.body && 'detail' in err.body
						? String((err.body as { detail: unknown }).detail)
						: err.message;
				return fail(err.status, { error: msg });
			}
			throw err;
		}
	}
};
