import { fail, redirect } from '@sveltejs/kit';

export function load() {
	return {};
}

export const actions = {
	default: async ({ request, fetch }) => {
		const data = await request.formData();
		const username = String(data.get('username') ?? '');
		const email = String(data.get('email') ?? '');
		const password = String(data.get('password') ?? '');
		const confirmPassword = String(data.get('confirm_password') ?? '');

		if (password !== confirmPassword) {
			return fail(400, { error: 'Passwords do not match' });
		}

		const response = await fetch('http://localhost:8000/api/users/register', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				username,
				email,
				password
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
				errorMessage = Object.values(payload).flat().join(' ') || errorMessage;
			}
		} catch {
			if (response.status === 409) {
				errorMessage = 'Username or email already exists';
			}
		}

		return fail(response.status, { error: errorMessage });
	}
};
