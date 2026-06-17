<script lang="ts">
	import type { Device } from '$lib/types/device';
	import { enhance } from '$app/forms';
	import toast from 'svelte-french-toast';
	import { fade } from 'svelte/transition';
	import { deviceStore } from '$lib/stores/devices.svelte';

	let { device }: { device: Device } = $props();
	let loading = $state(false);
</script>

<div class="flex items-center justify-between">
	<span class="text-sm">State: {device.current_state > 0 ? 'On' : 'Off'}</span>
	<form
		method="POST"
		action="?/control"
		use:enhance={({ formData }) => {
			loading = true;
			const actionType = formData.get('actionType');

			return async ({ result }) => {
				loading = false;
				if (result.type === 'failure') {
					toast.error((result.data?.error as string) || 'Action failed');
				} else if (result.type === 'success') {
					const targetState = actionType === 'turn_on' ? 1 : 0;
					deviceStore.updateDeviceState(device.id, { current_state: targetState });
				}
			};
		}}
	>
		<input type="hidden" name="deviceId" value={device.id} />
		<input
			type="hidden"
			name="actionType"
			value={device.current_state > 0 ? 'turn_off' : 'turn_on'}
		/>
		<button
			type="submit"
			disabled={loading}
			class="relative flex h-8 min-w-22 items-center justify-center rounded-md bg-accent px-3 py-1.5 text-sm text-surface hover:bg-accent-hover disabled:opacity-50"
		>
			{#if loading}
				<span
					transition:fade={{ duration: 150 }}
					class="absolute inline-block h-4 w-4 animate-spin rounded-full border-2 border-surface border-r-transparent"
				></span>
			{/if}
			<span class="transition-opacity duration-150 {loading ? 'opacity-0' : ''}">
				{device.current_state > 0 ? 'Turn Off' : 'Turn On'}
			</span>
		</button>
	</form>
</div>
