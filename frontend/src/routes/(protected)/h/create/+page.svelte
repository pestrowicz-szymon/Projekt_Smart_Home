<script lang="ts">
	import { resolve } from '$app/paths';
	import FormField from '$lib/components/FormField.svelte';
	import type { PageProps } from './$types';

	let { form }: PageProps = $props();
</script>

<svelte:head>
	<title>Create a home</title>
</svelte:head>

<div class="mx-auto max-w-md px-4 py-10">
	<a
		href={resolve('/h')}
		class="mb-4 inline-block text-sm text-foreground-muted hover:text-foreground"
	>
		&larr; Back
	</a>

	<h1 class="mb-2 text-2xl">Create a home</h1>
	<p class="mb-6 text-foreground-muted">
		Give your home a name. You'll be the owner and can invite members later.
	</p>

	<form method="POST" class="flex flex-col">
		<FormField
			name="name"
			type="text"
			required
			label="Name"
			placeholder="e.g. My Apartment"
			value={form?.values?.name ?? ''}
		/>
		<FormField
			name="description"
			type="text"
			label="Description (optional)"
			placeholder="Short description"
			value={form?.values?.description ?? ''}
		/>

		{#if form?.error}
			<p class="mb-3 text-danger">{form.error}</p>
		{/if}

		<button type="submit" class="rounded-md bg-accent py-2 text-surface hover:bg-accent-hover">
			Create home
		</button>
	</form>
</div>
