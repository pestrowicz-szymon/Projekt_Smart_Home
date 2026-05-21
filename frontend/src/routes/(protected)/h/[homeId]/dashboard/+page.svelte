<script lang="ts">
	import type { PageProps } from './$types';
	let { data }: PageProps = $props();

	const displayName = $derived(data.user.first_name || data.user.username);

	const hasHome = false;
</script>

<svelte:head>
	<title>Dashboard</title>
</svelte:head>

<div class="flex w-screen flex-col gap-4 bg-accent">
	<h1 class="text-2xl font-bold">Dashboard</h1>
	<p>Welcome, {displayName}!</p>
</div>
