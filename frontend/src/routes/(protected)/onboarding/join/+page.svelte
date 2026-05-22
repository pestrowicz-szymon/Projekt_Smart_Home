<script lang="ts">
	import { resolve } from '$app/paths';
	import { invalidateAll } from '$app/navigation';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	let copiedField = $state<string | null>(null);

	async function copy(value: string, field: string) {
		try {
			await navigator.clipboard.writeText(value);
			copiedField = field;
			setTimeout(() => {
				if (copiedField === field) copiedField = null;
			}, 1500);
		} catch {
			copiedField = null;
		}
	}
</script>

<svelte:head>
	<title>Join a home</title>
</svelte:head>

<div class="mx-auto max-w-md px-4 py-10">
	<a
		href={resolve('/onboarding')}
		class="mb-4 inline-block text-sm text-foreground-muted hover:text-foreground"
	>
		&larr; Back
	</a>

	<h1 class="mb-2 text-2xl">Join a home</h1>
	<p class="mb-6 text-foreground-muted">
		Ask the owner to add you. They'll need one of the values below.
	</p>

	<section class="mb-6 rounded-lg border border-line bg-surface-raised p-4">
		<h2 class="mb-3 text-md font-medium text-foreground">Share with the owner</h2>

		<ul class="flex flex-col gap-3">
			<li class="flex items-center justify-between gap-3">
				<div class="min-w-0">
					<p class="text-xs text-foreground-subtle">Email</p>
					<p class="truncate text-foreground">{data.user.email}</p>
				</div>
				<button
					type="button"
					onclick={() => copy(data.user.email, 'email')}
					class="shrink-0 rounded-md border border-line bg-surface px-3 py-1.5 text-sm hover:border-line-accent"
				>
					{copiedField === 'email' ? 'Copied' : 'Copy'}
				</button>
			</li>
		</ul>
	</section>

	<section class="mb-6 rounded-lg border border-line bg-surface-raised p-4 opacity-60">
		<div class="mb-2 flex items-center justify-between">
			<h2 class="text-md font-medium text-foreground">Have an invite code?</h2>
			<span class="rounded-pill bg-secondary-soft px-2 py-0.5 text-xs text-secondary">
				Coming soon
			</span>
		</div>
		<input
			type="text"
			placeholder="ABCD-1234"
			disabled
			class="w-full cursor-not-allowed"
			aria-label="Invite code"
		/>
	</section>

	<button
		type="button"
		onclick={() => invalidateAll()}
		class="w-full rounded-md bg-accent py-2 text-surface hover:bg-accent-hover"
	>
		I've been added — continue
	</button>
</div>
