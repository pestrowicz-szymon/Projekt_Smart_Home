<script lang="ts">
	import DeviceRefresher from '$lib/components/DeviceRefresher.svelte';

	let { children, data } = $props();
</script>

<DeviceRefresher initialDevices={data.devices} />
{@render children()}
