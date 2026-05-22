<script>
	import './layout.css';
	import NavProgress from '$lib/components/NavProgress.svelte';
	import { Toaster } from 'svelte-french-toast';

	let { children } = $props();
</script>

<Toaster />
<NavProgress />

<div class="flex min-h-dvh flex-col">
	<main class="flex-1">
		{@render children()}
	</main>
</div>
