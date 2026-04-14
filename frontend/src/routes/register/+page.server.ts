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

		if (password !== password2) {
			return fail(400, { error: 'Passwords do not match' });
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

		let errorMessage = 'Registration failed';

		try {
			const payload = await response.json();
			const payloadText = JSON.stringify(payload).toLowerCase();

			if (
				(payloadText.includes('username') && payloadText.includes('exist')) ||
				(payloadText.includes('email') && payloadText.includes('exist')) ||
				payloadText.includes('already')
			) {
				errorMessage = 'Username or email already exists';
			} else if (typeof payload === 'object' && payload !== null) {
				errorMessage = Object.values(payload)
					.flatMap((value) => (Array.isArray(value) ? value : [String(value)]))
					.join(' ')
					.trim() || errorMessage;
			}
		} catch {
			if (response.status === 409) {
				errorMessage = 'Username or email already exists';
			}
		}

		return fail(response.status, { error: errorMessage });
	}
};
