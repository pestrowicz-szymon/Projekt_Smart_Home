<script lang="ts">
	import type { PageProps } from './$types';
	import { enhance } from '$app/forms';
	import CpuIcon from '$lib/components/icons/CpuIcon.svelte';
	import ZapIcon from '$lib/components/icons/ZapIcon.svelte';

	let { data, form }: PageProps = $props();

	const unassignedGateways = $derived(data.gateways.filter((g) => !g.home));
	const myGateways = $derived(data.gateways.filter((g) => g.home));
</script>

<div class="p-4 max-w-2xl mx-auto space-y-8">
	<header>
		<h1 class="text-2xl font-bold">Gateways</h1>
		<p class="text-gray-500">Manage your Smart Home Hubs and discovery.</p>
	</header>

	{#if form?.error}
		<div class="p-3 bg-red-100 text-red-700 rounded-lg">
			{form.error}
		</div>
	{/if}

	<section class="space-y-4">
		<h2 class="text-lg font-semibold flex items-center gap-2">
			<ZapIcon class="w-5 h-5 text-yellow-500" />
			Discovery (Nearby Hubs)
		</h2>
		<p class="text-sm text-gray-600">
			New hubs connected to your network will appear here. Claim them to add them to your home.
		</p>

		{#if unassignedGateways.length === 0}
			<div class="p-8 border-2 border-dashed rounded-xl text-center text-gray-400">
				No new gateways discovered. Make sure your hub is powered on and connected.
			</div>
		{:else}
			<div class="grid gap-4">
				{#each unassignedGateways as gateway}
					<div class="p-4 bg-white border rounded-xl shadow-sm flex items-center justify-between">
						<div class="flex items-center gap-3">
							<div class="p-3 bg-blue-50 text-blue-600 rounded-lg">
								<CpuIcon class="w-6 h-6" />
							</div>
							<div>
								<div class="font-medium text-gray-900">{gateway.hardware_id}</div>
								<div class="text-xs text-gray-500 uppercase tracking-wider">{gateway.status}</div>
							</div>
						</div>

						<form
							method="POST"
							action="?/claim"
							use:enhance
							class="flex flex-wrap items-center gap-3"
						>
							<input type="hidden" name="hardwareId" value={gateway.hardware_id} />

							<div class="flex flex-col gap-1">
								<label
									for="homeId-{gateway.id}"
									class="text-[10px] font-bold text-gray-400 uppercase">Home</label
								>
								<select
									id="homeId-{gateway.id}"
									name="homeId"
									class="text-sm border rounded-md p-1.5 bg-gray-50"
									required
								>
									<option value="" disabled selected>Select...</option>
									{#each data.homes as home}
										<option value={home.id}>{home.name}</option>
									{/each}
								</select>
							</div>

							<div class="flex flex-col gap-1">
								<label
									for="pairingCode-{gateway.id}"
									class="text-[10px] font-bold text-gray-400 uppercase">PIN</label
								>
								<input
									id="pairingCode-{gateway.id}"
									type="text"
									name="pairingCode"
									placeholder="000000"
									maxlength="6"
									pattern="[0-9]{'{'}6}"
									class="w-20 text-sm border rounded-md p-1.5 bg-gray-50 font-mono text-center"
									required
								/>
							</div>

							<button
								type="submit"
								class="mt-4 px-4 py-1.5 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 transition-colors"
							>
								Claim
							</button>
						</form>
					</div>
				{/each}
			</div>
		{/if}
	</section>

	<section class="space-y-4">
		<h2 class="text-lg font-semibold">My Gateways</h2>
		<div class="grid gap-4">
			{#each myGateways as gateway}
				<div class="p-4 bg-gray-50 border rounded-xl flex items-center justify-between opacity-80">
					<div class="flex items-center gap-3">
						<div class="p-3 bg-gray-200 text-gray-600 rounded-lg">
							<CpuIcon class="w-6 h-6" />
						</div>
						<div>
							<div class="font-medium text-gray-900">{gateway.hardware_id}</div>
							<div class="text-xs text-gray-500">
								Assigned to <span class="font-semibold">{gateway.home_name || 'Your Home'}</span>
							</div>
						</div>
					</div>
					<div class="flex items-center gap-2">
						<span
							class="w-2 h-2 rounded-full {gateway.status === 'online'
								? 'bg-green-500'
								: 'bg-gray-400'}"
						></span>
						<span class="text-xs font-medium uppercase text-gray-500">{gateway.status}</span>
					</div>
				</div>
			{/each}

			{#if myGateways.length === 0}
				<p class="text-sm text-gray-400 italic">No gateways assigned yet.</p>
			{/if}
		</div>
	</section>
</div>
