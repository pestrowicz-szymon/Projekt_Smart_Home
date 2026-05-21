import { fail, redirect } from '@sveltejs/kit';
import type { PageServerLoad, Actions } from './$types';
import { ApiError, register } from '$lib/server/endpoints';
import type { RegisterPayload } from '$lib/types/auth';

type RegisterActionData = {
	formError?: string; // global error: API failure, network, unexpected
	fieldErrors: Record<string, string>; // per-field validation errors
	values: {
		username: string;
		first_name: string;
		last_name: string;
		email: string;
	};
};

function registerFail(
	status: number,
	partial: { formError?: string; fieldErrors?: Record<string, string> },
	values: RegisterActionData['values']
) {
	return fail(status, {
		formError: partial.formError,
		fieldErrors: partial.fieldErrors ?? {},
		values
	});
}

function extractFieldErrors(apiErrorBody: unknown): Record<string, string> {
	if (typeof apiErrorBody !== 'object' || apiErrorBody === null) {
		return {};
	}

	const fieldErrors: Record<string, string> = {};
	for (const [key, value] of Object.entries(apiErrorBody)) {
		if (typeof value === 'string') {
			fieldErrors[key] = value;
		} else if (Array.isArray(value) && value.every((item) => typeof item === 'string')) {
			fieldErrors[key] = value.join(' ');
		}
	}
	return fieldErrors;
}

export const load: PageServerLoad = () => {
	return {};
};

export const actions: Actions = {
	default: async ({ request, fetch }) => {
		const data = await request.formData();

		const payload: RegisterPayload = {
			username: String(data.get('username') ?? ''),
			first_name: String(data.get('first_name') ?? ''),
			last_name: String(data.get('last_name') ?? ''),
			email: String(data.get('email') ?? ''),
			password: String(data.get('password') ?? ''),
			password2: String(data.get('password2') ?? '')
		};

		const fieldErrors: Record<string, string> = {};

		if (!payload.first_name.trim()) fieldErrors.first_name = 'Name is required';
		if (!payload.last_name.trim()) fieldErrors.last_name = 'Surname is required';
		if (!payload.username.trim()) fieldErrors.first_name = 'First name is required';
		if (!payload.email) fieldErrors.email = 'Email is required';
		if (!payload.password) fieldErrors.password = 'Password is required';
		if (!payload.password2) fieldErrors.password2 = 'Confirm password is required';

		const cached_values = {
			first_name: payload.first_name,
			last_name: payload.last_name,
			username: payload.username,
			email: payload.email
		};

		if (Object.keys(fieldErrors).length > 0) {
			return registerFail(400, { fieldErrors }, cached_values);
		}

		if (payload.password !== payload.password2) {
			return registerFail(
				400,
				{ fieldErrors: { password2: 'Passwords do not match' } },
				cached_values
			);
		}

		try {
			await register(fetch, payload);
			throw redirect(303, '/login');
		} catch (error) {
			if (error instanceof ApiError) {
				// If backend returns per-field errors, map them; otherwise use formError
				const fieldErrors = extractFieldErrors(error.body);
				return registerFail(
					error.status,
					{
						formError: Object.keys(fieldErrors).length ? undefined : error.message,
						fieldErrors
					},
					cached_values
				);
			}
			throw error; // rethrow non-API errors (redirect, real bug)
		}
	}
};
