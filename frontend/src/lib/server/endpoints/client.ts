import { API_URL } from '$env/static/private';
import { createLogger } from '../logger';

const log = createLogger('api-client');

export class ApiError extends Error {
	constructor(
		public status: number,
		public body: unknown,
		message?: string
	) {
		super(message ?? `API error ${status}`);
	}
}

type FetchFn = typeof fetch;

interface RequestOptions {
	method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
	body?: unknown;
	token?: string;
}

export async function apiFetch<T>(
	fetch: FetchFn,
	path: string,
	{ method = 'GET', body, token }: RequestOptions = {}
): Promise<T> {
	const startTime = Date.now();
	const url = `${API_URL}${path}`;

	const headers: Record<string, string> = {};
	if (body !== undefined) headers['Content-Type'] = 'application/json';
	if (token) headers['Authorization'] = `Bearer ${token}`;

	log.debug({ method, path, headers }, `📤 Request: ${method} ${path}`);
	if (body) log.debug({ body }, `Request body`);

	let res: Response;
	try {
		res = await fetch(url, {
			method,
			headers,
			body: body === undefined ? undefined : JSON.stringify(body)
		});
	} catch (error) {
		const duration = Date.now() - startTime;
		log.error(
			{ method, path, error, duration },
			`❌ Request failed: ${method} ${path} (${duration}ms)`
		);
		throw error;
	}

	const text = await res.text();
	const data = text ? safeJson(text) : null;
	const duration = Date.now() - startTime;

	if (res.ok) {
		log.info(
			{ method, path, status: res.status, duration },
			`✅ Success: ${method} ${path} - ${res.status} (${duration}ms)`
		);
		if (data) log.debug({ data }, `Response data`);
		return data as T;
	}

	log.error(
		{ method, path, status: res.status, duration, error: data },
		`❌ Error: ${method} ${path} - ${res.status} (${duration}ms)`
	);
	throw new ApiError(res.status, data);
}

function safeJson(text: string): unknown {
	try {
		return JSON.parse(text);
	} catch {
		return text;
	}
}
