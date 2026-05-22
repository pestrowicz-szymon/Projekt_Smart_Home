<script lang="ts">
	import { invalidateAll } from '$app/navigation';
	import FormField from '$lib/components/FormField.svelte';
	import type { PageProps } from './$types';

	let { data, form }: PageProps = $props();

	const home = $derived(data.home);
	const canManage = $derived(data.canManage);

	const nameValue = $derived(form?.values?.name ?? home.name);
	const descriptionValue = $derived(form?.values?.description ?? home.description);

	$effect(() => {
		if (form?.success) invalidateAll();
	});
</script>

<svelte:head><title>General · {home.name}</title></svelte:head>

<div>
	{#if !canManage}
		<p class="mb-4 rounded-md border border-line bg-surface-raised p-3 text-sm text-foreground-muted">
			Only owners and admins can edit these fields.
		</p>
	{/if}

	<form method="POST" class="flex flex-col">
		<FormField
			name="name"
			type="text"
			required
			label="Name"
			value={nameValue}
			disabled={!canManage}
		/>
		<FormField
			name="description"
			type="text"
			label="Description"
			value={descriptionValue}
			disabled={!canManage}
		/>

		{#if form?.error}
			<p class="mb-3 text-danger">{form.error}</p>
		{/if}
		{#if form?.success}
			<p class="mb-3 text-success">Saved.</p>
		{/if}

		<button
			type="submit"
			disabled={!canManage}
			class="self-start rounded-md bg-accent px-4 py-2 text-surface hover:bg-accent-hover disabled:cursor-not-allowed disabled:opacity-50"
		>
			Save changes
		</button>
	</form>
</div>
