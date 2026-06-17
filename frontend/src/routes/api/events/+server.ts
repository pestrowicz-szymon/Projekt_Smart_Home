import { env } from '$env/dynamic/private';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ cookies }) => {
	const token = cookies.get('session');

	if (!token) {
		return new Response('Unauthorized', { status: 401 });
	}

	const url = `${env.API_URL}/api/devices/events/`;
	console.log(`[SSE Proxy] Connecting to: ${url}`);

	try {
		const response = await fetch(url, {
			headers: {
				Authorization: `Bearer ${token}`
			}
		});

		if (!response.ok) {
			const errorText = await response.text().catch(() => 'No error body');
			console.error(`[SSE Proxy] Backend error: ${response.status} ${errorText}`);
			return new Response(`Backend error: ${response.status}`, { status: response.status });
		}

		if (!response.body) {
			console.error(`[SSE Proxy] Backend returned 200 but no body`);
			return new Response('No stream body', { status: 500 });
		}

		console.log(`[SSE Proxy] Connected successfully, piping stream`);

		// Directly return the body from the backend fetch.
		// SvelteKit handles ReadableStream as response body.
		return new Response(response.body, {
			headers: {
				'Content-Type': 'text/event-stream',
				'Cache-Control': 'no-cache',
				Connection: 'keep-alive',
				'X-Accel-Buffering': 'no'
			}
		});
	} catch (err: unknown) {
		const message = err instanceof Error ? err.message : 'Unknown error';
		console.error(`[SSE Proxy] Fetch failed:`, message);
		return new Response(`Internal Server Error: ${message}`, { status: 500 });
	}
};
