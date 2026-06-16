export interface User {
	id: number;
	username: string;
	email: string;
	first_name: string;
	last_name: string;
	home_memberships: HomeMembership[];
}

export interface LoginResponse {
	access?: string;
	refresh?: string;
	user?: User;
	mfa_required?: boolean;
	mfa_token?: string;
	expires_at?: string;
}

export interface RegisterPayload {
	username: string;
	email: string;
	password: string;
	password2: string;
	first_name: string;
	last_name: string;
}

export interface HomeMembership {
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
