<script lang="ts">
	import { invalidateAll } from '$app/navigation';
	import FormField from '$lib/components/FormField.svelte';
	import { CpuIcon } from '$lib/components/icons';
	import { DEVICE_TYPE_LABEL, DEVICE_TYPES, type DeviceStatus } from '$lib/types/device';
	import type { PageProps } from './$types';

	let { data, form }: PageProps = $props();

	const home = $derived(data.home);
	const devices = $derived(data.devices);
	const canManage = $derived(data.canManageDevices);
	const isOwner = $derived(data.isOwner);

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

	$effect(() => {
		if (form?.success || form?.deleted) invalidateAll();
	});
</script>

<svelte:head><title>Devices · {home.name}</title></svelte:head>

<div class="mx-auto max-w-2xl px-4 py-6">
	<h1 class="mb-1 text-2xl">Devices</h1>
	<p class="mb-6 text-foreground-muted">Things connected to {home.name}.</p>

	{#if devices.length === 0}
		<div class="mb-6 rounded-lg border border-line bg-surface-raised p-6 text-center">
			<p class="mb-1 text-foreground">No devices yet.</p>
			<p class="text-sm text-foreground-muted">
				{canManage ? 'Add your first device below.' : 'Ask the home owner to add devices.'}
			</p>
		</div>
	{:else}
		<ul class="mb-8 divide-y divide-line overflow-hidden rounded-md border border-line bg-surface-raised">
			{#each devices as device (device.id)}
				<li class="flex items-center gap-3 px-4 py-3">
					<span class="rounded-md bg-accent-soft p-2 text-accent">
						<CpuIcon class="h-5 w-5" />
					</span>
					<div class="min-w-0 flex-1">
						<p class="truncate text-foreground">{device.name}</p>
						<p class="truncate text-xs text-foreground-subtle">
							{DEVICE_TYPE_LABEL[device.device_type]} · {device.hardware_id}
						</p>
					</div>
					<span
						class="shrink-0 rounded-pill px-2 py-0.5 text-xs {statusStyles[device.status]}"
					>
						{device.status}
					</span>
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
				</li>
			{/each}
		</ul>
	{/if}

	{#if canManage}
		<section class="rounded-lg border border-line bg-surface-raised p-4">
			<h2 class="mb-1 text-md font-medium text-foreground">Add device</h2>
			<p class="mb-4 text-sm text-foreground-muted">
				Register a new device by giving it a name and the hardware ID printed on it.
			</p>

			<form method="POST" action="?/create" class="flex flex-col">
				<FormField
					name="name"
					type="text"
					required
					label="Name"
					placeholder="e.g. Living room light"
					value={form?.values?.name ?? ''}
				/>

				<label class="mb-3 flex flex-col gap-1">
					<span class="text-sm">Device type</span>
					<select name="device_type" required>
						<option value="" disabled selected={!form?.values?.device_type}>Pick one…</option>
						{#each DEVICE_TYPES as type (type)}
							<option value={type} selected={form?.values?.device_type === type}>
								{DEVICE_TYPE_LABEL[type]}
							</option>
						{/each}
					</select>
				</label>

				<FormField
					name="hardware_id"
					type="text"
					required
					label="Hardware ID"
					placeholder="e.g. esp32-aa-bb"
					value={form?.values?.hardware_id ?? ''}
				/>

				<label class="mb-4 flex items-center gap-2 text-sm">
					<input name="is_active" type="checkbox" checked />
					Active
				</label>

				{#if form?.error}
					<p class="mb-3 text-danger">{form.error}</p>
				{/if}
				{#if form?.success}
					<p class="mb-3 text-success">Device added.</p>
				{/if}

				<button
					type="submit"
					class="self-start rounded-md bg-accent px-4 py-2 text-surface hover:bg-accent-hover"
				>
					Add device
				</button>
			</form>
		</section>
	{:else}
		<p class="rounded-md border border-line bg-surface-raised p-4 text-sm text-foreground-muted">
			Only the owner and members with device-management permission can add devices.
		</p>
	{/if}
</div>
