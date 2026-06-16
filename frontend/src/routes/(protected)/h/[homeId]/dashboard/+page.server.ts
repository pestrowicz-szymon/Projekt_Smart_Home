import type { Actions, PageServerLoad } from './$types';
import { sendDeviceAction } from '$lib/server/endpoints/devices';
import { listHomeDevices } from '$lib/server/endpoints/homes';
import { listRooms } from '$lib/server/endpoints/rooms';
import { fail } from '@sveltejs/kit';
import type { Device, Room } from '$lib/types/device';

export const load: PageServerLoad = async ({ params, locals, fetch, depends }) => {
	const homeId = Number(params.homeId);

	if (isNaN(homeId) || homeId <= 0) {
		throw new Error('Invalid home ID');
	}

	depends('app:devices');

	const [devices, rooms] = await Promise.all([
		listHomeDevices(fetch, locals.token!, homeId).then((ds) => ds.sort((a, b) => a.id - b.id)),
		listRooms(fetch, locals.token!)
	]);

	// Filter rooms by home and group devices
	const homeRooms = rooms.filter((r) => r.home === homeId);
	const devicesByRoom = groupDevicesByRoom(devices, homeRooms);

	return {
		devices,
		rooms: homeRooms,
		devicesByRoom
	};
};

function groupDevicesByRoom(
	devices: Device[],
	rooms: Room[]
): { room: Room | null; devices: Device[] }[] {
	const grouped: { [key: number]: Device[] } = { 0: [] };

	// Group devices
	devices.forEach((device) => {
		const roomId = device.room_id ?? device.room?.id ?? 0;
		if (!grouped[roomId]) grouped[roomId] = [];
		grouped[roomId].push(device);
	});

	// Build result with rooms
	const result: { room: Room | null; devices: Device[] }[] = [];

	// Add rooms with devices first
	rooms.forEach((room) => {
		if (grouped[room.id]) {
			result.push({ room, devices: grouped[room.id] });
		}
	});

	// Add unassigned devices last
	if (grouped[0].length > 0) {
		result.push({ room: null, devices: grouped[0] });
	}

	return result;
}

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
