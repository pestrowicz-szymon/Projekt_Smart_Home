export interface Room {
	id: number;
	home: number;
	name: string;
	description: string;
	created_at: string;
	updated_at: string;
}

export interface CreateRoomPayload {
	home_id: number;
	name: string;
	description: string;
}

export interface UpdateRoomPayload {
	home_id: number;
	name: string;
	description: string;
}

export interface PatchRoomPayload {
	home_id?: number;
	name?: string;
	description?: string;
}
