import { fail, redirect } from '@sveltejs/kit';
import type { Actions } from './$types';
import { addMember, patchMemberRole, removeMember } from '$lib/server/endpoints/homes';
import { ApiError } from '$lib/server/endpoints/client';
import type { HomeRole } from '$lib/types/home';

const ROLES: HomeRole[] = ['admin', 'member', 'viewer'];

export const actions: Actions = {
	remove: async ({ request, params, fetch, locals }) => {
		if (!locals.token) throw redirect(303, '/login');

		const data = await request.formData();
		const memberId = Number(data.get('member_id'));

		if (!Number.isInteger(memberId) || memberId <= 0) {
			return fail(400, { error: 'Invalid member id', action: 'remove' });
		}

		try {
			await removeMember(fetch, locals.token, Number(params.homeId), memberId);
			return { success: true, action: 'remove', removed: memberId };
		} catch (err) {
			if (err instanceof ApiError) {
				const msg =
					typeof err.body === 'object' && err.body && 'detail' in err.body
						? String((err.body as { detail: unknown }).detail)
						: err.message;
				return fail(err.status, { error: msg, action: 'remove' });
			}
			throw err;
		}
	},

	updateRole: async ({ request, params, fetch, locals }) => {
		if (!locals.token) throw redirect(303, '/login');

		const data = await request.formData();
		const memberId = Number(data.get('member_id'));
		const roleRaw = String(data.get('role') ?? 'member');

		if (!Number.isInteger(memberId) || memberId <= 0) {
			return fail(400, { error: 'Invalid member id', action: 'updateRole' });
		}
		if (!ROLES.includes(roleRaw as HomeRole)) {
			return fail(400, { error: 'Invalid role', action: 'updateRole' });
		}

		try {
			await patchMemberRole(
				fetch,
				locals.token,
				Number(params.homeId),
				memberId,
				roleRaw as HomeRole
			);
			return { success: true, action: 'updateRole', updated: memberId };
		} catch (err) {
			if (err instanceof ApiError) {
				const msg =
					typeof err.body === 'object' && err.body && 'detail' in err.body
						? String((err.body as { detail: unknown }).detail)
						: err.message;
				return fail(err.status, { error: msg, action: 'updateRole' });
			}
			throw err;
		}
	}
};
