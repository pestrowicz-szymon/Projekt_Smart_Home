<script lang="ts">
	import type { PageProps, ActionData } from './$types';
	import type { Device, Room, DeviceGroup } from '$lib/types/device';
	import DeviceCard from '$lib/components/DeviceCard.svelte';
	import { Thermometer, Light, Lock } from '$lib/components/devices';
	import { deviceStore } from '$lib/stores/devices.svelte';

	let { data }: { data: PageProps['data']; form: ActionData } = $props();

	const displayName = $derived(data.user.first_name || data.user.username);

	const devicesByRoom = $derived.by((): DeviceGroup[] => {
		const rooms = data.rooms;
		const devices = deviceStore.devices;

		const grouped: { [key: number]: Device[] } = { 0: [] };

		// Group devices
		devices.forEach((device) => {
			const roomId = device.room_id ?? device.room?.id ?? 0;
			if (!grouped[roomId]) grouped[roomId] = [];
			grouped[roomId].push(device);
		});

		// Build result with rooms
		const result: { room: Room | null; devices: Device[] }[] = [];

		// Add rooms with devices first
		rooms.forEach((room) => {
			if (grouped[room.id]) {
				result.push({ room, devices: grouped[room.id] });
			}
		});

		// Add unassigned devices last
		if (grouped[0].length > 0) {
			result.push({ room: null, devices: grouped[0] });
		}

		return result;
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

		{#if devicesByRoom.length === 0}
			<div class="rounded-lg border border-line bg-surface-raised p-6 text-center">
				<p class="text-foreground">No devices found in this home.</p>
				<p class="text-sm text-foreground-muted">Go to the Devices page to add some.</p>
			</div>
		{:else}
			{#each devicesByRoom as group (group.room?.id ?? 'unassigned')}
				<div class="mb-6">
					<h3 class="mb-3 text-lg font-medium text-foreground">
						{group.room?.name ?? 'Unassigned'}
					</h3>
					<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
						{#each group.devices as device (device.id)}
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
				</div>
			{/each}
		{/if}
	</section>
</div>
