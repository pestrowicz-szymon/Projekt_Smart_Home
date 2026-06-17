<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { deviceStore } from '$lib/stores/devices.svelte';
	import type { Device } from '$lib/types/device';

	interface Props {
		initialDevices: Device[];
		homeId: number;
		enabled?: boolean;
	}

	let { initialDevices, homeId, enabled = true }: Props = $props();

	onMount(() => {
		if (enabled) {
			deviceStore.init(initialDevices, homeId);
		}
	});

	onDestroy(() => {
		deviceStore.cleanup();
	});
</script>

{#if deviceStore.status === 'connecting'}
	<div class="fixed top-0 left-0 z-50 h-1 w-full bg-blue-500/20">
		<div class="h-full w-1/3 animate-pulse bg-blue-500"></div>
	</div>
{/if}
