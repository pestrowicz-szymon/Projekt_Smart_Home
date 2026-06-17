<script lang="ts">
	import type { PageProps } from './$types';
	import { enhance } from '$app/forms';
	import { CpuIcon, ZapIcon, GateIcon } from '$lib/components/icons';

	let { data, form }: PageProps = $props();

	const unassignedGateways = $derived(data.gateways.filter((g) => !g.home));
	const myGateways = $derived(data.gateways.filter((g) => g.home));
</script>

<svelte:head>
	<title>Gateways</title>
</svelte:head>

<div class="space-y-8">
	<header>
		<div class="mb-2 flex items-center gap-3">
			<div class="rounded-xl bg-accent-soft p-3 text-accent">
				<GateIcon class="w-8 h-8" />
			</div>
			<div>
				<h1 class="text-2xl font-bold">Gateways</h1>
				<p class="text-foreground-muted">Manage your Smart Home Hubs.</p>
			</div>
		</div>
	</header>

	{#if form?.error}
		<div
			class="p-4 bg-danger-soft text-danger border border-danger-edge rounded-xl text-sm font-medium"
		>
			{form.error}
		</div>
	{/if}

	<section class="space-y-4">
		<h2
			class="px-2 text-sm font-bold uppercase tracking-wider text-foreground-subtle flex items-center gap-2"
		>
			<ZapIcon class="w-4 h-4 text-secondary" />
			Discovery (Nearby Hubs)
		</h2>

		{#if unassignedGateways.length === 0}
			<div class="p-10 border-2 border-dashed border-line rounded-xl text-center">
				<p class="text-foreground-subtle font-medium">No new gateways discovered</p>
				<p class="text-xs text-foreground-subtle mt-1">
					Make sure your hub is connected to the network.
				</p>
			</div>
		{:else}
			<div class="grid gap-4">
				{#each unassignedGateways as gateway}
					<div
						class="overflow-hidden rounded-xl border border-line bg-surface-raised p-4 shadow-sm"
					>
						<div class="flex items-center justify-between mb-6">
							<div class="flex items-center gap-3">
								<div class="p-3 bg-accent-soft text-accent rounded-lg">
									<CpuIcon class="w-6 h-6" />
								</div>
								<div>
									<div class="font-bold text-foreground">{gateway.hardware_id}</div>
									<div
										class="text-[10px] font-bold uppercase tracking-widest text-foreground-subtle"
									>
										{gateway.status}
									</div>
								</div>
							</div>
						</div>

						<form
							method="POST"
							action="?/claim"
							use:enhance
							class="flex flex-col gap-4 bg-surface-sunken p-4 rounded-lg border border-line"
						>
							<input type="hidden" name="hardwareId" value={gateway.hardware_id} />

							<div class="grid grid-cols-2 gap-4">
								<div class="flex flex-col gap-1.5">
									<label
										for="homeId-{gateway.id}"
										class="text-[10px] font-bold text-foreground-subtle uppercase px-1"
										>Assign to Home</label
									>
									<select id="homeId-{gateway.id}" name="homeId" class="text-sm bg-white" required>
										<option value="" disabled selected>Select...</option>
										{#each data.homes as home}
											<option value={home.id}>{home.name}</option>
										{/each}
									</select>
								</div>

								<div class="flex flex-col gap-1.5">
									<label
										for="pairingCode-{gateway.id}"
										class="text-[10px] font-bold text-foreground-subtle uppercase px-1"
										>Pairing PIN</label
									>
									<input
										id="pairingCode-{gateway.id}"
										type="text"
										name="pairingCode"
										placeholder="000000"
										maxlength="6"
										pattern="[0-9]{'{'}6}"
										class="text-sm bg-white font-mono text-center tracking-widest"
										required
									/>
								</div>
							</div>

							<button
								type="submit"
								class="w-full py-2.5 bg-accent text-white text-sm font-bold rounded-md hover:bg-accent-hover transition-colors shadow-sm"
							>
								Claim Gateway
							</button>
						</form>
					</div>
				{/each}
			</div>
		{/if}
	</section>

	<section class="space-y-4">
		<h2 class="px-2 text-sm font-bold uppercase tracking-wider text-foreground-subtle">
			My Gateways
		</h2>
		<div class="grid gap-3">
			{#each myGateways as gateway}
				<div
					class="p-4 bg-surface-raised border border-line rounded-xl flex items-center justify-between"
				>
					<div class="flex items-center gap-3">
						<div
							class="p-2.5 bg-surface-sunken text-foreground-muted rounded-lg border border-line"
						>
							<CpuIcon class="w-5 h-5" />
						</div>
						<div>
							<div class="font-semibold text-foreground">{gateway.hardware_id}</div>
							<div class="text-xs text-foreground-muted">
								Assigned to <span class="text-accent">{gateway.home_name || 'Your Home'}</span>
							</div>
						</div>
					</div>
					<div
						class="flex items-center gap-2 px-2 py-1 bg-surface-sunken rounded-pill border border-line"
					>
						<span
							class="w-2 h-2 rounded-full {gateway.status === 'online'
								? 'bg-success shadow-[0_0_8px_rgba(74,124,89,0.5)]'
								: 'bg-foreground-subtle'}"
						></span>
						<span class="text-[10px] font-bold uppercase text-foreground-muted"
							>{gateway.status}</span
						>
					</div>
				</div>
			{/each}

			{#if myGateways.length === 0}
				<div class="p-6 bg-surface-sunken border border-line border-dashed rounded-xl text-center">
					<p class="text-sm text-foreground-subtle italic">No gateways assigned yet.</p>
				</div>
			{/if}
		</div>
	</section>
</div>
