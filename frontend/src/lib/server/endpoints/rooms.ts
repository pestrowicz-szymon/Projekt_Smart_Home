import { apiFetch } from './client';
import { createLogger } from '../logger';
import type { Room, CreateRoomPayload, UpdateRoomPayload, PatchRoomPayload } from '$lib/types/room';

type FetchFn = typeof fetch;
const log = createLogger('rooms-endpoint');

export function listRooms(fetch: FetchFn, token: string) {
	log.debug('Fetching list of rooms');
	return apiFetch<Room[]>(fetch, '/api/devices/rooms/', { token });
}

export function getRoomsByHome(fetch: FetchFn, token: string, homeId: number) {
	log.debug({ homeId }, `Fetching rooms for home ${homeId}`);
	return apiFetch<Room[]>(fetch, `/api/devices/rooms/?home_id=${homeId}`, { token });
}

export function getRoom(fetch: FetchFn, token: string, id: number) {
	log.debug({ id }, `Fetching room ${id}`);
	return apiFetch<Room>(fetch, `/api/devices/rooms/${id}/`, { token });
}

export function createRoom(fetch: FetchFn, token: string, body: CreateRoomPayload) {
	log.debug({ body }, 'Creating new room');
	return apiFetch<Room>(fetch, '/api/devices/rooms/', { method: 'POST', body, token });
}

export function updateRoom(fetch: FetchFn, token: string, id: number, body: UpdateRoomPayload) {
	log.debug({ id, body }, `Updating room ${id}`);
	return apiFetch<Room>(fetch, `/api/devices/rooms/${id}/`, { method: 'PUT', body, token });
}

export function patchRoom(fetch: FetchFn, token: string, id: number, body: PatchRoomPayload) {
	log.debug({ id, body }, `Partially updating room ${id}`);
	return apiFetch<Room>(fetch, `/api/devices/rooms/${id}/`, { method: 'PATCH', body, token });
}

export function deleteRoom(fetch: FetchFn, token: string, id: number) {
	log.debug({ id }, `Deleting room ${id}`);
	return apiFetch<null>(fetch, `/api/devices/rooms/${id}/`, { method: 'DELETE', token });
}
