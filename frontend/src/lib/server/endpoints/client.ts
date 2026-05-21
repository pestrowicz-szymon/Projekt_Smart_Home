import { API_URL } from '$env/static/private';

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
	const headers: Record<string, string> = {};
	if (body !== undefined) headers['Content-Type'] = 'application/json';
	if (token) headers['Authorization'] = `Bearer ${token}`;

	const res = await fetch(`${API_URL}${path}`, {
		method,
		headers,
		body: body === undefined ? undefined : JSON.stringify(body)
	});

	const text = await res.text();
	const data = text ? safeJson(text) : null;

	if (!res.ok) throw new ApiError(res.status, data);
	return data as T;
}

function safeJson(text: string): unknown {
	try {
		return JSON.parse(text);
	} catch {
		return text;
	}
}
