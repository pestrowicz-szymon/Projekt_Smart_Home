import type { Actions, PageServerLoad } from './$types';
import { sendDeviceAction } from '$lib/server/endpoints/devices';
import { fail } from '@sveltejs/kit';

export const load: PageServerLoad = async ({ depends }) => {
	depends('app:devices');
	return {};
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
