<script lang="ts">
	import type { PageData } from './$types';

	interface User {
		id: number;
		username: string;
		email: string;
		first_name: string;
		last_name: string;
	}

	interface Device {
		id: number;
		name: string;
		type: 'Light' | 'Thermostat' | 'Door Lock' | 'Camera' | 'Smoke Sensor' | 'Blind';
		room: string;
		status: string;
	}

	let { data }: { data: PageData & { user: User | null } } = $props();

	const displayName = $derived(data.user?.first_name || data.user?.username || 'User');

	let nextId = 100;
	let deleteMode = $state(false);

	let devices = $state<Device[]>([
		{ id: 1, name: 'Ceiling Aura', type: 'Light', room: 'Living Room', status: 'On' },
		{ id: 2, name: 'Heat Pilot', type: 'Thermostat', room: 'Hallway', status: '21 C' },
		{ id: 3, name: 'Front Guard', type: 'Door Lock', room: 'Entrance', status: 'Locked' },
		{ id: 4, name: 'Night Eye', type: 'Camera', room: 'Garage', status: 'Recording' }
	]);

	const mockCatalog: Device[] = [
		{ id: 101, name: 'Kitchen Beam', type: 'Light', room: 'Kitchen', status: 'Off' },
		{ id: 102, name: 'Bedroom Sense', type: 'Thermostat', room: 'Bedroom', status: '20 C' },
		{ id: 103, name: 'Patio Watch', type: 'Camera', room: 'Garden', status: 'Standby' },
		{ id: 104, name: 'Roof Alert', type: 'Smoke Sensor', room: 'Attic', status: 'Idle' },
		{ id: 105, name: 'Sunshade Pro', type: 'Blind', room: 'Dining Room', status: 'Half Open' }
	];

	function addMockDevice(device: Omit<Device, 'id'>) {
		devices = [...devices, { id: nextId++, ...device }];
	}

	function removeDevice(deviceId: number) {
		devices = devices.filter((device) => device.id !== deviceId);
	}
</script>

<svelte:head>
	<title>Dashboard</title>
</svelte:head>

<main class="home-shell">
	<section class="dashboard-grid">
		<article class="welcome-card">
			<p class="eyebrow">Smart Home</p>
			<h1>Welcome, {displayName}!</h1>
			<p class="subtitle">Your connected home at a glance.</p>
		</article>

		{#each devices as device (device.id)}
			<article class="device-card" class:deletable={deleteMode}>
				<p class="device-type">{device.type}</p>
				<p class="status">{device.status}</p>
				<p class="device-name">{device.name}</p>
				<p class="device-room">{device.room}</p>
				<div class="device-actions">
					{#if deleteMode}
						<button class="delete-btn" type="button" onclick={() => removeDevice(device.id)}>
							Delete
						</button>
					{/if}
				</div>
			</article>
		{/each}

		<article class="add-device-card">
			<details class="add-menu">
				<summary>
					<span class="plus-icon">+</span>
					<span class="add-label">Add Device</span>
				</summary>
				<div class="device-menu">
					<div class="menu-header">
						<h3>Select a Device</h3>
						<button
							type="button"
							class="close-btn"
							onclick={(e: Event) => {
								if (e.target && e.target instanceof HTMLElement) {
									const details = e.target.closest('details');
									if (details) {
										details.open = false;
									}
								}
							}}
						>
							✕
						</button>
					</div>
					<ul>
						{#each mockCatalog as mock (mock.id)}
							<li>
								<button type="button" onclick={() => addMockDevice(mock)}>
									+ {mock.name} ({mock.type})
								</button>
							</li>
						{/each}
					</ul>
				</div>
			</details>
		</article>

		<aside class="settings-card">
			<h2>Settings</h2>
			<p>Manage dashboard behavior and account session.</p>

			<button type="button" class:danger={deleteMode} onclick={() => (deleteMode = !deleteMode)}>
				{deleteMode ? 'Delete Mode: ON' : 'Delete Mode: OFF'}
			</button>

			<form method="POST" action="?/logout">
				<button type="submit" class="logout-btn">Logout</button>
			</form>
		</aside>
	</section>
</main>

<style>
	.home-shell {
		min-height: 100vh;
		display: flex;
		align-items: flex-start;
		justify-content: flex-start;
		padding: 1.25rem;
		background: linear-gradient(130deg, #0f172a 0%, #1e293b 50%, #111827 100%);
	}

	.dashboard-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(12rem, 1fr));
		gap: 1.25rem;
		width: 100%;
	}

	.welcome-card {
		padding: 1.4rem;
		border-radius: 1rem;
		background: rgba(15, 23, 42, 0.92);
		color: #e2e8f0;
		box-shadow: 0 18px 45px rgba(0, 0, 0, 0.35);
		display: grid;
		gap: 0.9rem;
		grid-column: 1 / 2;
	}

	.device-card {
		padding: 1.2rem;
		border-radius: 1rem;
		background: linear-gradient(160deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95));
		color: #e2e8f0;
		box-shadow: 0 18px 45px rgba(0, 0, 0, 0.35);
		border: 1px solid rgba(148, 163, 184, 0.3);
		display: grid;
		gap: 0.7rem;
	}

	.device-card.deletable {
		border-color: rgba(248, 113, 113, 0.55);
		box-shadow:
			0 18px 45px rgba(0, 0, 0, 0.35),
			inset 0 0 0 1px rgba(248, 113, 113, 0.2);
	}

	.add-device-card {
		padding: 0;
		border-radius: 1rem;
		background: rgba(30, 41, 59, 0.6);
		color: #e2e8f0;
		box-shadow: 0 18px 45px rgba(0, 0, 0, 0.35);
		border: 2px dashed rgba(148, 163, 184, 0.4);
		display: flex;
		align-items: center;
		justify-content: center;
		min-height: 6rem;
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.add-device-card:hover {
		border-color: rgba(148, 163, 184, 0.6);
		background: rgba(30, 41, 59, 0.75);
	}

	.add-device-card .add-menu {
		width: 100%;
		display: flex;
		align-items: center;
		justify-content: center;
		position: relative;
	}

	.add-device-card .add-menu summary {
		width: 100%;
		padding: 1.2rem;
		text-align: center;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: 0.3rem;
		cursor: pointer;
	}

	.plus-icon {
		font-size: 1.8rem;
		font-weight: 700;
		color: #22d3ee;
	}

	.add-label {
		font-size: 0.85rem;
		font-weight: 600;
		color: #cbd5e1;
	}

	.settings-card {
		padding: 1.4rem;
		border-radius: 1rem;
		background: rgba(15, 23, 42, 0.92);
		color: #e2e8f0;
		box-shadow: 0 18px 45px rgba(0, 0, 0, 0.35);
		height: max-content;
		display: grid;
		gap: 0.9rem;
		grid-column: -1 / -2;
		grid-row: 1;
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

	h2 {
		margin: 0;
		font-size: 1.05rem;
		color: #e2e8f0;
	}

	.subtitle {
		margin: 0;
		color: #94a3b8;
	}

	.add-menu {
		position: relative;
	}

	.menu-header {
		display: none;
	}

	.add-menu[open] .menu-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 0.7rem 0.9rem;
		/* margin-bottom: 3px; */
		/* border-bottom: 1px solid rgba(56, 189, 248, 0.3); */
		/* position: fixed; */
		/* left: 50%; */
		/* top: calc(50% - 3.15rem); */
		/* transform: translateX(-50%); */
		z-index: 51;
		width: 18rem;
		background: rgba(2, 6, 23, 0.98);
		/* border: 1px solid rgba(56, 189, 248, 0.35); */
		/* border-radius: 0.7rem 0.7rem 0 0; */
	}

	.add-menu[open] ul {
		border-radius: 0 0 0.7rem 0.7rem;
		overflow-y: auto;

		/* margin-top: 3.15rem; */
	}

	.add-menu[open] li {
		padding: 0.55rem 0.7rem;
		/* border-top: 1px solid rgba(56, 189, 248, 0.3); */
	}

	.menu-header h3 {
		margin: 0;
		font-size: 0.9rem;
		color: #e2e8f0;
	}

	.close-btn {
		padding: 0.2rem 0.5rem;
		margin: 0;
		background: transparent;
		color: #94a3b8;
		border: none;
		font-size: 1.2rem;
		cursor: pointer;
		transition: color 0.15s ease;
	}

	.close-btn:hover {
		color: #cbd5e1;
	}

	.add-menu summary::-webkit-details-marker {
		display: none;
	}

	.add-menu .device-menu {
		margin: 0;
		padding: 0.55rem;
		list-style: none;
		display: grid;
		gap: 0.4rem;
		border-radius: 0.7rem;
		background: rgba(2, 6, 23, 0.98);
		border: 1px solid rgba(56, 189, 248, 0.35);
		position: fixed;
		z-index: 50;
		min-width: 18rem;
		max-height: 24rem;
		box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
		left: 50%;
		top: 50%;
		transform: translate(-50%, -50%);
	}

	.add-device-card .add-menu .device-menu {
		position: fixed;
		left: 50%;
		top: 50%;
		transform: translate(-50%, -50%);
		margin: 0;
		max-height: 24rem;
	}

	.add-menu ul button {
		width: 100%;
		text-align: left;
		padding: 0.55rem 0.7rem;
		margin: 0;
		background: rgba(15, 23, 42, 0.95);
		color: #e2e8f0;
		border: 1px solid rgba(148, 163, 184, 0.3);
		border-radius: 0.55rem;
	}

	.device-room {
		margin: 0;
		font-size: 0.7rem;
		letter-spacing: 0.03em;
		color: #64748b;
		text-align: center;
	}

	.device-name {
		margin: 0;
		font-weight: 600;
		color: #e2e8f0;
		font-size: 0.85rem;
		text-align: center;
	}

	.device-actions {
		display: flex;
		align-items: center;
		justify-content: flex-end;
		gap: 0.5rem;
		margin-top: auto;
	}

	.device-type {
		margin: 0;
		font-size: 0.7rem;
		letter-spacing: 0.06em;
		text-transform: uppercase;
		color: #94a3b8;
		text-align: center;
	}

	.status {
		margin: 0;
		font-size: 1.8rem;
		font-weight: 700;
		color: #22c55e;
		text-align: center;
		letter-spacing: 0.02em;
	}

	button {
		margin-top: 0;
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

	.delete-btn {
		padding: 0.4rem 0.6rem;
		font-size: 0.85rem;
		background: #f87171;
		color: #450a0a;
	}

	button.danger {
		background: #f87171;
		color: #450a0a;
	}

	.logout-btn {
		width: 100%;
		background: #22d3ee;
		color: #083344;
	}

	button:hover {
		transform: translateY(-1px);
		filter: brightness(1.05);
	}

	@media (max-width: 900px) {
		.dashboard-grid {
			grid-template-columns: 1fr;
		}

		.add-menu ul {
			left: 0;
			right: auto;
		}
	}
</style>
