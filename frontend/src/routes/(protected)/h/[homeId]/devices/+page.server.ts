import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { createDevice, deleteDevice, listDevices } from '$lib/server/endpoints/devices';
import { ApiError } from '$lib/server/endpoints/client';
import { DEVICE_TYPES, type DeviceType } from '$lib/types/device';

export const load: PageServerLoad = async ({ params, fetch, locals }) => {
	if (!locals.token) throw redirect(303, '/login');

	const homeId = Number(params.homeId);
	const all = await listDevices(fetch, locals.token);
	const devices = all.filter((d) => d.home.id === homeId);

	return { devices };
};

export const actions: Actions = {
	create: async ({ request, params, fetch, locals }) => {
		if (!locals.token) throw redirect(303, '/login');

		const data = await request.formData();
		const name = String(data.get('name') ?? '').trim();
		const deviceTypeRaw = String(data.get('device_type') ?? '');
		const hardwareId = String(data.get('hardware_id') ?? '').trim();
		const isActive = data.get('is_active') === 'on';

		const values = { name, device_type: deviceTypeRaw, hardware_id: hardwareId };

		if (!name) return fail(400, { error: 'Name is required', values });
		if (!DEVICE_TYPES.includes(deviceTypeRaw as DeviceType)) {
			return fail(400, { error: 'Pick a device type', values });
		}
		if (!hardwareId) {
			return fail(400, { error: 'Hardware ID is required', values });
		}

		try {
			await createDevice(fetch, locals.token, {
				home_id: Number(params.homeId),
				name,
				device_type: deviceTypeRaw as DeviceType,
				hardware_id: hardwareId,
				is_active: isActive
			});
			return { success: true };
		} catch (err) {
			if (err instanceof ApiError) {
				const body = err.body;
				let msg = err.message;
				if (body && typeof body === 'object') {
					if ('hardware_id' in body)
						msg = `Hardware ID: ${(body as Record<string, unknown>).hardware_id}`;
					else if ('detail' in body) msg = String((body as { detail: unknown }).detail);
					else if ('home_id' in body) msg = String((body as Record<string, unknown>).home_id);
				}
				return fail(err.status, { error: msg, values });
			}
			throw err;
		}
	},

	delete: async ({ request, fetch, locals }) => {
		if (!locals.token) throw redirect(303, '/login');

		const data = await request.formData();
		const idRaw = String(data.get('id') ?? '');
		const id = Number(idRaw);
		if (!Number.isInteger(id) || id <= 0) return fail(400, { error: 'Invalid device id' });

		try {
			await deleteDevice(fetch, locals.token, id);
			return { deleted: true };
		} catch (err) {
			if (err instanceof ApiError) {
				const body = err.body;
				const msg =
					body && typeof body === 'object' && 'detail' in body
						? String((body as { detail: unknown }).detail)
						: err.message;
				return fail(err.status, { error: msg });
			}
			throw err;
		}
	}
};
