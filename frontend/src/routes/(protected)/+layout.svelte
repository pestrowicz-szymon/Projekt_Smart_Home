<script lang="ts">
	import BottomNav from '$lib/components/BottomNav.svelte';
	import MoreSheet from '$lib/components/MoreSheet.svelte';
	import type { LayoutProps } from './$types';

	let { children, data }: LayoutProps = $props();

	let moreOpen = $state(false);
</script>

<div class="flex min-h-dvh flex-col">
	<main class="mx-auto flex w-full max-w-3xl flex-1 flex-col px-4 pt-6 pb-24 md:pb-6">
		{@render children()}
	</main>
	<BottomNav onMoreClick={() => (moreOpen = true)} />
	<MoreSheet bind:open={moreOpen} user={data.user} />
</div>
