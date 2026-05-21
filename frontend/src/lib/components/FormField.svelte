<!-- src/lib/components/FormField.svelte -->
<script lang="ts">
	import type { HTMLInputAttributes } from 'svelte/elements';

	interface Props extends HTMLInputAttributes {
		name: string; // make required (it's optional on plain input)
		label: string; // your custom addition
		error?: string; // your custom addition
	}

	let { name, label, error, ...rest }: Props = $props();
</script>

<div class="mb-4 flex flex-col">
	<label for={name} class="text-md">{label}</label>
	<input class="form-input" {name} {...rest} aria-invalid={error ? 'true' : undefined} />
	{#if error}
		<p class="mt-1 text-danger">{error}</p>
	{/if}
</div>
