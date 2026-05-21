import type { User } from './auth';

export type HomeRole = 'owner' | 'admin' | 'member' | 'viewer';

export interface HomeMember {
	id: number;
	user: User;
	role: HomeRole;
	can_manage_devices: boolean;
	created_at: string;
}

export interface Home {
	id: number;
	name: string;
	description: string;
	owner: User;
	members: HomeMember[];
	devices_count: number;
	created_at: string;
	updated_at: string;
}

export interface CreateHomePayload {
	name: string;
	description?: string;
}
