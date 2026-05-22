<script lang="ts">
	import type { PageProps } from './$types';

	let { data, form }: PageProps = $props();

	const home = $derived(data.home);
	const isOwner = $derived(data.isOwner);

	let confirmation = $state('');
</script>

<svelte:head><title>Danger zone · {home.name}</title></svelte:head>

<div class="flex flex-col gap-6">
	<section class="rounded-lg border border-line bg-surface-raised p-4 opacity-60">
		<div class="mb-2 flex items-center justify-between">
			<h2 class="text-md font-medium text-foreground">Leave home</h2>
			<span class="rounded-pill bg-secondary-soft px-2 py-0.5 text-xs text-secondary">
				Coming soon
			</span>
		</div>
		<p class="text-sm text-foreground-muted">
			Remove yourself from this home. You'll lose access until the owner re-invites you.
		</p>
	</section>

	{#if isOwner}
		<section class="rounded-lg border border-danger-edge bg-danger-soft p-4">
			<h2 class="mb-1 text-md font-medium text-danger">Delete this home</h2>
			<p class="mb-3 text-sm text-foreground-muted">
				This permanently deletes <strong class="text-foreground">{home.name}</strong>, all its devices,
				and all member records. This cannot be undone.
			</p>

			<form method="POST" action="?/delete" class="flex flex-col gap-3">
				<label class="flex flex-col gap-1">
					<span class="text-sm">
						Type <strong class="text-foreground">{home.name}</strong> to confirm
					</span>
					<input
						name="confirmation"
						type="text"
						bind:value={confirmation}
						autocomplete="off"
						required
					/>
					<input type="hidden" name="expected" value={home.name} />
				</label>

				{#if form?.error}
					<p class="text-danger">{form.error}</p>
				{/if}

				<button
					type="submit"
					disabled={confirmation !== home.name}
					class="self-start rounded-md bg-danger px-4 py-2 text-surface hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
				>
					Delete home permanently
				</button>
			</form>
		</section>
	{:else}
		<section class="rounded-lg border border-line bg-surface-raised p-4">
			<h2 class="mb-1 text-md font-medium text-foreground">Delete home</h2>
			<p class="text-sm text-foreground-muted">Only the home owner can delete this home.</p>
		</section>
	{/if}
</div>
