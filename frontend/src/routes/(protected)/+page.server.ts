import { redirect } from '@sveltejs/kit';

// src/routes/(protected)/devices/+page.server.ts
export async function load({ cookies, fetch }) {
	const token = cookies.get('session');

	if (!token) {
		throw redirect(303, '/login');
	}

	try {
		const res = await fetch('http://backend/api/devices', {
			headers: { Authorization: `Bearer ${token}` }
		});

		if (res.status === 401 || res.status === 403) {
			cookies.delete('session', { path: '/' });
			throw redirect(303, '/login');
		}

		if (!res.ok) {
			throw new Error(`Failed to load devices: ${res.status}`);
		}

		return { devices: await res.json() };
	} catch (error) {
		if (error instanceof Response) {
			throw error;
		}

		cookies.delete('session', { path: '/' });
		throw redirect(303, '/login');
	}
}
