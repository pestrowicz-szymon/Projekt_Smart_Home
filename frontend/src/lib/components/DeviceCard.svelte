<script lang="ts">
	import type { Snippet } from 'svelte';
	import { CpuIcon } from '$lib/components/icons';
	import { DEVICE_TYPE_LABEL, type DeviceStatus, type Device } from '$lib/types/device';

	let { device, children }: { device: Device; children?: Snippet } = $props();

	const statusStyles: Record<DeviceStatus, string> = {
		online: 'bg-success-soft text-success',
		offline: 'bg-danger-soft text-danger',
		unknown: 'bg-surface-sunken text-foreground-muted'
	};
</script>

<div class="flex flex-col rounded-lg border border-line bg-surface-raised p-4">
	<div class="mb-2 flex items-center justify-between">
		<div class="flex items-center gap-2">
			<span class="rounded-md bg-accent-soft p-2 text-accent">
				<CpuIcon class="h-5 w-5" />
			</span>
			<h3 class="font-medium text-foreground">{device.name}</h3>
		</div>
		<span class="rounded-pill px-2 py-0.5 text-xs {statusStyles[device.status]}">
			{device.status}
		</span>
	</div>

	<p class="mb-4 text-sm text-foreground-muted">
		{DEVICE_TYPE_LABEL[device.device_type]}
	</p>

	<div class="mt-auto">
		<div class="rounded-md bg-surface-sunken p-3">
			{@render children?.()}
		</div>
	</div>
</div>
