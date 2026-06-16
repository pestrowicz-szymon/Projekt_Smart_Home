import { error } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';
import { canManageDevices, canManageHome, isHomeOwner } from '$lib/server/permissions';
import { listHomeDevices } from '$lib/server/endpoints/homes';
import { listRooms } from '$lib/server/endpoints/rooms';

export const load: LayoutServerLoad = async ({ params, locals, cookies, fetch }) => {
	const id = Number(params.homeId);
	const home = locals.homes?.find((h) => h.id === id);
	if (!home) throw error(404, 'Home not found');

	if (locals.activeHome?.id !== id) {
		cookies.set('activeHomeId', String(id), {
			path: '/',
			httpOnly: true,
			sameSite: 'lax'
		});
	}

	const [devices, rooms] = await Promise.all([
		listHomeDevices(fetch, locals.token!, id).then((ds) => ds.sort((a, b) => a.id - b.id)),
		listRooms(fetch, locals.token!)
	]);

	const homeRooms = rooms.filter((r) => r.home === id);

	const userId = locals.user!.id;
	return {
		home,
		devices,
		rooms: homeRooms,
		canManage: canManageHome(home, userId),
		canManageDevices: canManageDevices(home, userId),
		isOwner: isHomeOwner(home, userId)
	};
};
