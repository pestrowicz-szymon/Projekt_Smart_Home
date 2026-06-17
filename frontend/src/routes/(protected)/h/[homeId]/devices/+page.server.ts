import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { deleteDevice, updateDevice } from '$lib/server/endpoints/devices';
import { listRooms } from '$lib/server/endpoints/rooms';
import { listHomeDevices } from '$lib/server/endpoints/homes';
import { ApiError } from '$lib/server/endpoints/client';
import type { Device, Room } from '$lib/types/device';

export const load: PageServerLoad = async ({ params, fetch, locals, depends }) => {
	if (!locals.token) throw redirect(303, '/login');

	const homeId = Number(params.homeId);
	depends('app:devices');

	const [devices, rooms] = await Promise.all([
		listHomeDevices(fetch, locals.token, homeId).then((ds) => ds.sort((a, b) => a.id - b.id)),
		listRooms(fetch, locals.token)
	]);

	// Filter rooms by home and group devices
	const homeRooms = rooms.filter((r) => r.home === homeId);
	const devicesByRoom = groupDevicesByRoom(devices, homeRooms);

	return { devices, rooms: homeRooms, devicesByRoom };
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
	update: async ({ request, fetch, locals }) => {
		if (!locals.token) throw redirect(303, '/login');

		const data = await request.formData();
		const deviceId = Number(data.get('id'));
		const name = String(data.get('name') ?? '').trim();
		const roomIdRaw = String(data.get('room_id') ?? '').trim();
		const roomId = roomIdRaw ? Number(roomIdRaw) : null;

		if (!Number.isInteger(deviceId) || deviceId <= 0)
			return fail(400, { error: 'Invalid device id' });
		if (!name) return fail(400, { error: 'Name is required' });

		try {
			await updateDevice(fetch, locals.token, deviceId, {
				name,
				room_id: roomId
			});
			return { success: true, updated: deviceId };
		} catch (err) {
			if (err instanceof ApiError) {
				const body = err.body;
				let msg = err.message;
				if (body && typeof body === 'object') {
					if ('detail' in body) msg = String((body as { detail: unknown }).detail);
				}
				return fail(err.status, { error: msg });
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
