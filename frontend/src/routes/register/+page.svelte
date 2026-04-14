<script>
	import { resolve } from '$app/paths';
	let { form } = $props();
</script>

<svelte:head>
	<title>Register</title>
</svelte:head>

<div class="login-shell">
	<form method="POST" class="login-card">
		<h1>Smart Home Systems</h1>
		<p>Register for a new account.</p>

		<label>
			<input name="first_name" autocomplete="given-name" required placeholder="Name" />
		</label>

		<label>
			<input name="last_name" autocomplete="family-name" required placeholder="Surname" />
		</label>

		<label>
			<input name="username" autocomplete="username" required placeholder="Username" />
		</label>

		<label>
			<input name="email" type="email" placeholder="Email" required />
		</label>

		<label>
			<input
				name="password"
				type="password"
				autocomplete="new-password"
				required
				placeholder="Password"
			/>
		</label>

		<label>
			<input
				name="password2"
				type="password"
				autocomplete="new-password"
				required
				placeholder="Confirm Password"
			/>
		</label>

		{#if form?.error}
			<p class="error">{form.error}</p>
		{/if}

		<button type="submit">Register</button>
		<a class="sign-up" href={resolve('/login')}>Already have an account? Login</a>
	</form>
</div>

<style>
	.login-shell {
		min-height: 100vh;
		display: grid;
		place-items: center;
		padding: 1.5rem;
		background: linear-gradient(135deg, #111827 0%, #1f2937 45%, #0f172a 100%);
	}

	.login-card {
		width: min(100%, 24rem);
		display: grid;
		gap: 1rem;
		padding: 2rem;
		border-radius: 1.25rem;
		background: rgba(15, 23, 42, 0.9);
		color: white;
		box-shadow: 0 1.5rem 4rem rgba(0, 0, 0, 0.35);
		backdrop-filter: blur(16px);
	}

	.sign-up {
		background: transparent;
		color: #38bdf8;
		font-weight: 500;
		transition: background 0.2s;
	}

	.sign-up:hover {
		background: #fff;
	}

	h1,
	p {
		margin: 0;
	}

	label {
		display: grid;
		gap: 0.4rem;
	}

	input,
	button {
		font: inherit;
		border-radius: 0.8rem;
		border: 1px solid rgba(148, 163, 184, 0.35);
		padding: 0.85rem 1rem;
	}

	input {
		background: rgba(15, 23, 42, 0.7);
		color: white;
	}

	button {
		margin-top: 0.5rem;
		background: #38bdf8;
		color: #082f49;
		font-weight: 700;
		cursor: pointer;
	}

	.error {
		color: #fca5a5;
	}
</style>
