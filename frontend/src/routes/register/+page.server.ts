import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = () => {
	return {};
};

export const actions: Actions = {
	default: async ({ request, fetch }) => {
		const data = await request.formData();
		const username = String(data.get('username') ?? '');
		const firstName = String(data.get('first_name') ?? '');
		const lastName = String(data.get('last_name') ?? '');
		const email = String(data.get('email') ?? '');
		const password = String(data.get('password') ?? '');
		const password2 = String(data.get('password2') ?? '');

		const values = {
			username,
			first_name: firstName,
			last_name: lastName,
			email
		};

		const fieldErrors: Record<string, string> = {};

		if (!firstName.trim()) fieldErrors.first_name = 'Name is required';
		if (!lastName.trim()) fieldErrors.last_name = 'Surname is required';
		if (!username.trim()) fieldErrors.username = 'Username is required';
		if (!email.trim()) fieldErrors.email = 'Email is required';
		if (!password) fieldErrors.password = 'Password is required';
		if (!password2) fieldErrors.password2 = 'Confirm password is required';

		if (Object.keys(fieldErrors).length > 0) {
			return fail(400, {
				errors: fieldErrors,
				values
			});
		}

		if (password !== password2) {
			return fail(400, {
				errors: { password2: 'Passwords do not match' },
				values
			});
		}

		const response = await fetch('http://127.0.0.1:8000/api/users/register/', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				username,
				email,
				password,
				password2,
				first_name: firstName,
				last_name: lastName
			})
		});

		if (response.ok) {
			throw redirect(303, '/login');
		}

		const errors: Record<string, string> = {};

		try {
			const payload = await response.json();

			if (payload && typeof payload === 'object') {
				for (const [key, value] of Object.entries(payload)) {
					const text = Array.isArray(value)
						? value.map((item) => String(item)).join(' ')
						: String(value);

					if (key === 'non_field_errors' || key === 'detail') {
						errors.form = text || 'Registration failed';
					} else {
						errors[key] = text;
					}
				}
			}
		} catch {
			// Keep default message when backend does not return JSON.
		}

		if (Object.keys(errors).length === 0 && response.status === 400) {
			errors.form = 'Registration data is invalid. Please review your inputs.';
		}

		if (Object.keys(errors).length === 0) {
			errors.form = 'Registration failed. Please try again.';
		}

		return fail(response.status, { errors, values });
	}
};
