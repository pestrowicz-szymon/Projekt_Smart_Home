<script lang="ts">
	import BottomNav from '$lib/components/BottomNav.svelte';
	import MoreSheet from '$lib/components/MoreSheet.svelte';
	import type { LayoutProps } from './$types';

	let { children, data }: LayoutProps = $props();

	let moreOpen = $state(false);
</script>

<div class="flex min-h-dvh flex-col">
	<main class="flex-1">
		{@render children()}
	</main>
	<BottomNav onMoreClick={() => (moreOpen = true)} />
	<MoreSheet bind:open={moreOpen} user={data.user} />
</div>
