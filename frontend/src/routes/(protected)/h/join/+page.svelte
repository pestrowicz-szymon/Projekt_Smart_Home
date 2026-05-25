<script lang="ts">
	import { resolve } from '$app/paths';
	import { invalidateAll } from '$app/navigation';
	import FormField from '$lib/components/FormField.svelte';
	import type { PageProps } from './$types';

	let { data, form }: PageProps = $props();

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

<div class="flex flex-col">
	<a
		href={resolve('/h')}
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
					<p class="text-s text-foreground-subtle">UUID</p>
					<p class="truncate text-foreground">{data.user.id}</p>
				</div>
				<button
					type="button"
					onclick={() => copy(data.user.id, 'id')}
					class="shrink-0 rounded-md border border-line bg-surface px-3 py-1.5 text-sm hover:border-line-accent"
				>
					{copiedField === 'id' ? 'Copied' : 'Copy'}
				</button>
			</li>
		</ul>
	</section>

	<section class="mb-6 rounded-lg border border-line bg-surface-raised p-4">
		<h2 class="mb-3 text-md font-medium text-foreground">Have an invite code?</h2>
		<p class="mb-3 text-sm text-foreground-muted">
			The home owner can generate an invite code to add you instantly.
		</p>
		<form method="POST" action="?/redeem" class="flex flex-col gap-3">
			<FormField
				name="code"
				type="text"
				required
				label="Invite code"
				placeholder="Paste the code here"
				value={form?.values?.code ?? ''}
				autocomplete="off"
			/>

			{#if form?.error}
				<p class="text-danger">{form.error}</p>
			{/if}

			<button
				type="submit"
				class="rounded-md bg-accent px-4 py-2 text-surface hover:bg-accent-hover"
			>
				Join with code
			</button>
		</form>
	</section>

	<button
		type="button"
		onclick={() => invalidateAll()}
		class="w-full rounded-md bg-accent py-2 text-surface hover:bg-accent-hover"
	>
		I've been added — continue
	</button>
</div>
