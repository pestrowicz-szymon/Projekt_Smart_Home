<script lang="ts">
	import DeviceRefresher from '$lib/components/DeviceRefresher.svelte';

	let { children } = $props();
</script>

<DeviceRefresher />
{@render children()}
