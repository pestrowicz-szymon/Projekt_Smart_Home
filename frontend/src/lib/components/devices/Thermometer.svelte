<script lang="ts">
	import type { Device } from '$lib/types/device';

	let { device }: { device: Device } = $props();
</script>

<div class="text-center">
	<p class="text-2xl font-bold text-foreground">
		{device.current_state.toFixed(1)}°C
	</p>
	<p class="text-xs text-foreground-muted">Current Temperature</p>
</div>
