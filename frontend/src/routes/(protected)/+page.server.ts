// src/routes/(protected)/devices/+page.server.ts
export async function load({ cookies, fetch }) {
	const token = cookies.get('session');
	const res = await fetch('http://backend/api/devices', {
		headers: { Authorization: `Bearer ${token}` }
	});
	return { devices: await res.json() };
}
