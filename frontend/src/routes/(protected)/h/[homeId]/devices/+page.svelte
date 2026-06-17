<script lang="ts">
	import { invalidateAll } from '$app/navigation';
	import FormField from '$lib/components/FormField.svelte';
	import { CpuIcon } from '$lib/components/icons';
	import {
		DEVICE_TYPE_LABEL,
		DEVICE_TYPES,
		type DeviceStatus,
		type Device,
		type Room
	} from '$lib/types/device';
	import { deviceStore } from '$lib/stores/devices.svelte';
	import type { PageProps } from './$types';

	let { data, form }: PageProps = $props();

	const home = $derived(data.home);
	const rooms = $derived(data.rooms);
	const canManage = $derived(data.canManageDevices);
	const isOwner = $derived(data.isOwner);

	const devicesByRoom = $derived.by(() => {
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

	let editingId: number | null = $state(null);
	let editFormData: Partial<Device> | null = $state(null);

	const statusStyles: Record<DeviceStatus, string> = {
		online: 'bg-success-soft text-success',
		offline: 'bg-danger-soft text-danger',
		unknown: 'bg-surface-sunken text-foreground-muted'
	};

	function confirmDelete(name: string, event: SubmitEvent) {
		if (!confirm(`Delete "${name}"? This cannot be undone.`)) {
			event.preventDefault();
		}
	}

	function startEdit(device: Device) {
		editingId = device.id;
		editFormData = { ...device, room_id: device.room_id ?? device.room?.id ?? null };
	}

	function cancelEdit() {
		editingId = null;
		editFormData = null;
	}

	$effect(() => {
		if (form?.success || form?.deleted || form?.updated) {
			invalidateAll();
			cancelEdit();
		}
	});
</script>

<svelte:head><title>Devices · {home.name}</title></svelte:head>

<div class="flex flex-col">
	<h1 class="mb-1 text-2xl">Devices</h1>
	<p class="mb-6 text-foreground-muted">Things connected to {home.name}.</p>

	{#if !devicesByRoom || devicesByRoom.length === 0}
		<div class="mb-6 rounded-lg border border-line bg-surface-raised p-6 text-center">
			<p class="mb-1 text-foreground">No devices yet.</p>
			<p class="text-sm text-foreground-muted">
				{canManage
					? 'Connect a gateway to discover devices.'
					: 'Ask the home owner to connect a gateway.'}
			</p>
		</div>
	{:else}
		{#each devicesByRoom as group (group.room?.id ?? 'unassigned')}
			<div class="mb-6">
				<h2 class="mb-3 text-lg font-medium text-foreground">
					{group.room?.name ?? 'Unassigned'}
				</h2>
				<ul
					class="divide-y divide-line overflow-hidden rounded-md border border-line bg-surface-raised"
				>
					{#each group.devices as device (device.id)}
						<li class="px-4 py-3">
							{#if editingId === device.id && editFormData}
								<!-- Edit mode -->
								<form method="POST" action="?/update" class="flex flex-col gap-2">
									<input type="hidden" name="id" value={device.id} />

									<FormField
										name="name"
										type="text"
										required
										label="Device name"
										placeholder="e.g. Living room light"
										value={editFormData.name ?? ''}
									/>

									{#if rooms && rooms.length > 0}
										<label class="flex flex-col gap-1">
											<span class="text-sm">Room (optional)</span>
											<select name="room_id">
												<option value="">No room</option>
												{#each rooms as room (room.id)}
													<option value={room.id} selected={editFormData.room_id === room.id}>
														{room.name}
													</option>
												{/each}
											</select>
										</label>
									{/if}

									{#if form?.error}
										<p class="text-xs text-danger">{form.error}</p>
									{/if}

									<div class="flex gap-2">
										<button
											type="submit"
											class="rounded-md bg-accent px-3 py-1 text-xs text-surface hover:bg-accent-hover"
										>
											Save
										</button>
										<button
											type="button"
											onclick={cancelEdit}
											class="rounded-md border border-line px-3 py-1 text-xs hover:bg-surface-sunken"
										>
											Cancel
										</button>
									</div>
								</form>
							{:else}
								<!-- Display mode -->
								<div class="flex items-center gap-3">
									<span class="rounded-md bg-accent-soft p-2 text-accent">
										<CpuIcon class="h-5 w-5" />
									</span>
									<div class="min-w-0 flex-1">
										<p class="truncate text-foreground">{device.name}</p>
										<p class="truncate text-xs text-foreground-subtle">
											{DEVICE_TYPE_LABEL[device.device_type]} · {device.hardware_id}
										</p>
										<p class="truncate text-xs text-foreground-muted">
											Room: {device.room?.name ?? 'Unassigned'}
										</p>
									</div>
									<span
										class="shrink-0 rounded-pill px-2 py-0.5 text-xs {statusStyles[device.status]}"
									>
										{device.status}
									</span>
									{#if canManage}
										<button
											type="button"
											onclick={() => startEdit(device)}
											class="shrink-0 rounded-md px-2 py-1 text-xs text-accent hover:bg-accent-soft"
										>
											Edit
										</button>
									{/if}
									{#if isOwner}
										<form
											method="POST"
											action="?/delete"
											onsubmit={(e) => confirmDelete(device.name, e)}
										>
											<input type="hidden" name="id" value={device.id} />
											<button
												type="submit"
												class="shrink-0 rounded-md px-2 py-1 text-xs text-danger hover:bg-danger-soft"
												aria-label="Delete {device.name}"
											>
												Delete
											</button>
										</form>
									{/if}
								</div>
							{/if}
						</li>
					{/each}
				</ul>
			</div>
		{/each}
	{/if}
</div>
