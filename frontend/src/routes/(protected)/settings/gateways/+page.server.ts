import { error } from '@sveltejs/kit';
import type { PageServerLoad, Actions } from './$types';
import { listGateways, claimGateway } from '$lib/server/endpoints/devices';
import { listHomes } from '$lib/server/endpoints/homes';

export const load: PageServerLoad = async ({ fetch, locals }) => {
	const token = locals.token;
	if (!token) throw error(401, 'Unauthorized');

	try {
		const [gateways, homes] = await Promise.all([
			listGateways(fetch, token),
			listHomes(fetch, token)
		]);

		return {
			gateways,
			homes
		};
	} catch (e) {
		console.error('Failed to load gateways/homes:', e);
		return {
			gateways: [],
			homes: []
		};
	}
};

export const actions: Actions = {
	claim: async ({ request, fetch, locals }) => {
		const token = locals.token;
		if (!token) throw error(401, 'Unauthorized');

		const data = await request.formData();
		const hardwareId = data.get('hardwareId')?.toString();
		const homeId = Number(data.get('homeId'));
		const pairingCode = data.get('pairingCode')?.toString();

		if (!hardwareId || !homeId || !pairingCode) {
			return { success: false, error: 'Missing gateway, home ID or pairing code' };
		}

		try {
			await claimGateway(fetch, token, hardwareId, homeId, pairingCode);
			return { success: true };
		} catch (e: any) {
			console.error('Failed to claim gateway:', e);
			const detail = e.response?.data?.detail || 'Failed to claim gateway';
			return { success: false, error: detail };
		}
	}
};
