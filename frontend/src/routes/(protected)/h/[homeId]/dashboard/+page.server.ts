import type { Actions, PageServerLoad } from './$types';
import { listDevices, sendDeviceAction } from '$lib/server/endpoints/devices';
import { fail } from '@sveltejs/kit';

export const load: PageServerLoad = async ({ params, locals, fetch }) => {
	const allDevices = await listDevices(fetch, locals.token!);
	const homeId = Number(params.homeId);
	const devices = allDevices.filter((d) => d.home.id === homeId);

	return {
		devices
	};
};

export const actions: Actions = {
	control: async ({ request, locals, fetch }) => {
		const data = await request.formData();
		const deviceId = Number(data.get('deviceId'));
		const actionType = data.get('actionType') as string;

		if (!deviceId || !actionType) {
			return fail(400, { error: 'Invalid request' });
		}

		try {
			await sendDeviceAction(fetch, locals.token!, deviceId, actionType);
			return { success: true };
		} catch (e: unknown) {
			const errorMessage = e instanceof Error ? e.message : 'Failed to send action';
			return fail(500, { error: errorMessage });
		}
	}
};
