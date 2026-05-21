export interface User {
	id: number;
	username: string;
	email: string;
	first_name: string;
	last_name: string;
	home_memberships: HomeMebership[];
}

export interface LoginResponse {
	access: string;
	refresh: string;
	user?: User;
}

export interface RegisterPayload {
	username: string;
	email: string;
	password: string;
	password2: string;
	first_name: string;
	last_name: string;
}

export interface HomeMebership {
	id: number;
	home: Home;
	role: string;
	can_manage_devices: boolean;
	created_at: string;
}

export interface Home {
	id: number;
	name: string;
	description: string;
}
