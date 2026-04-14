<script lang="ts">
	import type { PageData } from './$types';

	interface User {
		id: number;
		username: string;
		email: string;
		first_name: string;
		last_name: string;
	}

	let { data }: { data: PageData & { user: User | null } } = $props();

	const displayName = $derived(data.user?.first_name || data.user?.username || 'User');
</script>

<svelte:head>
	<title>Dashboard</title>
</svelte:head>

<main class="home-shell">
	<section class="welcome-card">
		<p class="eyebrow">Smart Home</p>
		<h1>Welcome, {displayName}!</h1>
		<p class="subtitle">You are now logged in.</p>

		<form method="POST" action="?/logout">
			<button type="submit">Logout</button>
		</form>
	</section>
</main>

<style>
	.home-shell {
		min-height: 100vh;
		display: grid;
		place-items: center;
		padding: 1.5rem;
		background: linear-gradient(130deg, #0f172a 0%, #1e293b 50%, #111827 100%);
	}

	.welcome-card {
		width: min(100%, 34rem);
		padding: 2rem;
		border-radius: 1rem;
		background: rgba(15, 23, 42, 0.92);
		color: #e2e8f0;
		box-shadow: 0 18px 45px rgba(0, 0, 0, 0.35);
		display: grid;
		gap: 0.9rem;
	}

	.eyebrow {
		margin: 0;
		font-size: 0.82rem;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: #7dd3fc;
	}

	h1 {
		margin: 0;
		font-size: clamp(1.5rem, 4vw, 2rem);
		color: #f8fafc;
	}

	.subtitle {
		margin: 0;
		color: #94a3b8;
	}

	button {
		margin-top: 0.5rem;
		padding: 0.75rem 1rem;
		border: 1px solid transparent;
		border-radius: 0.75rem;
		background: #38bdf8;
		color: #082f49;
		font-weight: 700;
		font: inherit;
		cursor: pointer;
		transition:
			transform 0.15s ease,
			filter 0.15s ease;
	}

	button:hover {
		transform: translateY(-1px);
		filter: brightness(1.05);
	}
</style>
