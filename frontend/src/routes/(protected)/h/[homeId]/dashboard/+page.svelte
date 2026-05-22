<script lang="ts">
	import type { PageProps, ActionData } from './$types';
	import type { Device } from '$lib/types/device';
	import { untrack } from 'svelte';
	import DeviceCard from '$lib/components/DeviceCard.svelte';
	import { Thermometer, Light, Lock } from '$lib/components/devices';

	let { data }: { data: PageProps['data']; form: ActionData } = $props();

	const displayName = $derived(data.user.first_name || data.user.username);

	// Initialize with data.devices to avoid SSR flicker, sync with $effect
	let devices = $state<Device[]>(untrack(() => data.devices));
	$effect(() => {
		devices = data.devices;
	});
</script>

<svelte:head>
	<title>Dashboard</title>
</svelte:head>

<div class="flex flex-col">
	<h1 class="mb-1 text-2xl font-bold">Dashboard</h1>
	<p class="mb-6 text-foreground-muted">Welcome back, {displayName}!</p>

	<section class="mb-8">
		<h2 class="mb-4 text-xl font-medium">Your Devices</h2>

		{#if devices.length === 0}
			<div class="rounded-lg border border-line bg-surface-raised p-6 text-center">
				<p class="text-foreground">No devices found in this home.</p>
				<p class="text-sm text-foreground-muted">Go to the Devices page to add some.</p>
			</div>
		{:else}
			<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
				{#each devices as device (device.id)}
					<DeviceCard {device}>
						{#if device.device_type === 'thermometer'}
							<Thermometer {device} />
						{:else if device.device_type === 'light'}
							<Light {device} />
						{:else if device.device_type === 'lock'}
							<Lock {device} />
						{:else}
							<div class="text-center">
								<p class="text-lg font-medium text-foreground">
									State: {device.current_state}
								</p>
							</div>
						{/if}
					</DeviceCard>
				{/each}
			</div>
		{/if}
	</section>
</div>
