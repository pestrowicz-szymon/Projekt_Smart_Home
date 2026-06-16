<script lang="ts">
	import { onMount } from 'svelte';
	import { invalidate } from '$app/navigation';

	interface Props {
		intervalMs?: number;
		enabled?: boolean;
	}

	let { intervalMs = 1000, enabled = true }: Props = $props();

	onMount(() => {
		let interval: ReturnType<typeof setInterval>;

		function start() {
			interval = setInterval(() => {
				if (enabled) {
					invalidate('app:devices');
				}
			}, intervalMs);
		}

		if (enabled) {
			start();
		}

		return () => {
			clearInterval(interval);
		};
	});
</script>
