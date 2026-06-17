<script lang="ts">
	import BottomNav from '$lib/components/BottomNav.svelte';
	import MoreSheet from '$lib/components/MoreSheet.svelte';
	import type { LayoutProps } from './$types';

	let { children, data }: LayoutProps = $props();

	let moreOpen = $state(false);
</script>

<div class="flex min-h-dvh flex-col">
	<main class="mx-auto flex w-full flex-1 flex-col pt-6 pb-24 md:pb-6">
		<div class="mx-auto w-full max-w-2xl px-4">
			{@render children()}
		</div>
	</main>
	<BottomNav onMoreClick={() => (moreOpen = true)} />
	<MoreSheet bind:open={moreOpen} user={data.user} />
</div>
