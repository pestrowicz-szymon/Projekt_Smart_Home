<script lang="ts">
	import DeviceRefresher from '$lib/components/DeviceRefresher.svelte';
	import type { LayoutProps } from './$types';

	let { children, data }: LayoutProps = $props();
</script>

<DeviceRefresher initialDevices={data.devices} homeId={data.home.id} />
{@render children()}
