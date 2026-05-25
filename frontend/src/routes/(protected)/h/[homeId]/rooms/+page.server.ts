import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { listRooms, createRoom, updateRoom, deleteRoom } from '$lib/server/endpoints/rooms';
import { listHomeDevices } from '$lib/server/endpoints/homes';
import { ApiError } from '$lib/server/endpoints/client';

export const load: PageServerLoad = async ({ params, fetch, locals }) => {
	if (!locals.token) throw redirect(303, '/login');

	const homeId = Number(params.homeId);
	const [allRooms, devices] = await Promise.all([
		listRooms(fetch, locals.token),
		listHomeDevices(fetch, locals.token, homeId)
	]);

	const rooms = allRooms.filter((r) => r.home === homeId);

	// Count devices per room
	const deviceCount: Record<number, number> = {};
	rooms.forEach((room) => {
		deviceCount[room.id] = devices.filter((d) => d.room_id === room.id).length;
	});

	return { rooms, deviceCount };
};

export const actions: Actions = {
	create: async ({ request, params, fetch, locals }) => {
		if (!locals.token) throw redirect(303, '/login');

		const data = await request.formData();
		const name = String(data.get('name') ?? '').trim();
		const description = String(data.get('description') ?? '').trim();

		if (!name) return fail(400, { error: 'Room name is required' });

		try {
			await createRoom(fetch, locals.token, {
				home: Number(params.homeId),
				name,
				description: description || undefined
			});
			return { success: true };
		} catch (err) {
			if (err instanceof ApiError) {
				const body = err.body;
				let msg = err.message;
				if (body && typeof body === 'object') {
					if ('name' in body) msg = `Name: ${(body as Record<string, unknown>).name}`;
					else if ('detail' in body) msg = String((body as { detail: unknown }).detail);
				}
				return fail(err.status, { error: msg });
			}
			throw err;
		}
	},

	update: async ({ request, fetch, locals }) => {
		if (!locals.token) throw redirect(303, '/login');

		const data = await request.formData();
		const roomId = Number(data.get('id'));
		const name = String(data.get('name') ?? '').trim();
		const description = String(data.get('description') ?? '').trim();

		if (!roomId) return fail(400, { error: 'Invalid room id' });
		if (!name) return fail(400, { error: 'Room name is required' });

		try {
			await updateRoom(fetch, locals.token, roomId, {
				name,
				description: description || undefined
			});
			return { success: true, roomId };
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
		const roomId = Number(data.get('id'));

		if (!roomId) return fail(400, { error: 'Invalid room id' });

		try {
			await deleteRoom(fetch, locals.token, roomId);
			return { success: true, deleted: roomId };
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
	}
};
