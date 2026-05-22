import type { Home } from '$lib/types/home';

export function canManageHome(home: Home, userId: number): boolean {
	if (home.owner.id === userId) return true;
	const m = home.members.find((m) => m.user.id === userId);
	if (!m) return false;
	return m.role === 'admin' || m.can_manage_devices;
}

export function canManageDevices(home: Home, userId: number): boolean {
	if (home.owner.id === userId) return true;
	const m = home.members.find((m) => m.user.id === userId);
	if (!m) return false;
	return m.can_manage_devices;
}

export function isHomeOwner(home: Home, userId: number): boolean {
	return home.owner.id === userId;
}
