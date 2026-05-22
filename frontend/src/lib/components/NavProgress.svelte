<script lang="ts">
	import { navigating } from '$app/state';

	let visible = $state(false);
	let finishing = $state(false);
	let width = $state(0);

	let showTimer: ReturnType<typeof setTimeout> | null = null;
	let tickTimer: ReturnType<typeof setInterval> | null = null;
	let resetTimer: ReturnType<typeof setTimeout> | null = null;

	function start() {
		if (resetTimer) {
			clearTimeout(resetTimer);
			resetTimer = null;
		}
		if (showTimer || visible) return;

		// Defer showing so quick navigations don't flash a bar.
		showTimer = setTimeout(() => {
			showTimer = null;
			visible = true;
			finishing = false;
			width = 12;
			tickTimer = setInterval(() => {
				width = Math.min(90, width + (90 - width) * 0.1);
			}, 180);
		}, 120);
	}

	function end() {
		if (showTimer) {
			clearTimeout(showTimer);
			showTimer = null;
		}
		if (!visible) return;
		if (tickTimer) {
			clearInterval(tickTimer);
			tickTimer = null;
		}
		finishing = true;
		width = 100;
		resetTimer = setTimeout(() => {
			visible = false;
			finishing = false;
			width = 0;
			resetTimer = null;
		}, 350);
	}

	$effect(() => {
		if (navigating.to !== null) start();
		else end();
	});
</script>

<div class="pointer-events-none fixed inset-x-0 top-0 z-[100] h-[2px]" aria-hidden="true">
	{#if visible}
		<div
			class="h-full bg-accent transition-[width,opacity] duration-300 ease-out"
			style="width: {width}%; opacity: {finishing
				? 0
				: 1}; box-shadow: 0 0 6px var(--color-accent);"
		></div>
	{/if}
</div>
