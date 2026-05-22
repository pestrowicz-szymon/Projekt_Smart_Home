<script>
	import './layout.css';
	import NavProgress from '$lib/components/NavProgress.svelte';

	let { children } = $props();
</script>

<NavProgress />

<div class="flex min-h-dvh flex-col">
	<main class="flex-1">
		{@render children()}
	</main>
</div>
