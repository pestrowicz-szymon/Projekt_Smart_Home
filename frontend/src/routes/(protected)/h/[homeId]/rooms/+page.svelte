<script lang="ts">
	import { invalidateAll } from '$app/navigation';
	import FormField from '$lib/components/FormField.svelte';
	import type { PageProps } from './$types';

	let { data, form }: PageProps = $props();

	const rooms = $derived(data.rooms);
	const deviceCount = $derived(data.deviceCount);
	let editingId: number | null = $state(null);

	$effect(() => {
		if (form?.success) {
			invalidateAll();
			editingId = null;
		}
	});

	function confirmDelete(name: string, event: SubmitEvent) {
		if (!confirm(`Delete "${name}"? Devices in this room will become unassigned.`)) {
			event.preventDefault();
		}
	}
</script>

<svelte:head><title>Rooms</title></svelte:head>

<div class="flex flex-col gap-6">
	<div>
		<h1 class="mb-1 text-2xl">Rooms</h1>
		<p class="text-foreground-muted">Organize your devices by room.</p>
	</div>

	{#if rooms && rooms.length > 0}
		<ul class="divide-y divide-line overflow-hidden rounded-md border border-line bg-surface-raised">
			{#each rooms as room (room.id)}
				<li class="px-4 py-3">
					{#if editingId === room.id}
						<!-- Edit mode -->
						<form method="POST" action="?/update" class="flex flex-col gap-3">
							<input type="hidden" name="id" value={room.id} />

							<FormField
								name="name"
								type="text"
								required
								label="Room name"
								placeholder="e.g. Living room"
								value={form?.name ?? room.name}
							/>

							<textarea
								name="description"
								class="rounded-md border border-line bg-surface px-3 py-2 text-sm"
								placeholder="Optional description"
								rows="3"
							>
{room.description}</textarea>

							{#if form?.error}
								<p class="text-danger">{form.error}</p>
							{/if}

							<div class="flex gap-2">
								<button
									type="submit"
									class="rounded-md bg-accent px-3 py-1 text-xs text-surface hover:bg-accent-hover"
								>
									Save
								</button>
								<button
									type="button"
									onclick={() => (editingId = null)}
									class="rounded-md border border-line px-3 py-1 text-xs hover:bg-surface-sunken"
								>
									Cancel
								</button>
							</div>
						</form>
					{:else}
						<!-- Display mode -->
						<div class="flex items-start justify-between">
							<div class="min-w-0 flex-1">
								<h3 class="font-medium text-foreground">{room.name}</h3>
								{#if room.description}
									<p class="mt-1 text-sm text-foreground-muted">{room.description}</p>
								{/if}
								<p class="mt-2 text-xs text-foreground-subtle">
									{deviceCount[room.id] ?? 0} device{(deviceCount[room.id] ?? 0) !== 1 ? 's' : ''}
								</p>
							</div>

							<div class="flex flex-shrink-0 gap-2">
								<button
									type="button"
									onclick={() => (editingId = room.id)}
									class="rounded-md px-2 py-1 text-xs text-accent hover:bg-accent-soft"
								>
									Edit
								</button>
								<form method="POST" action="?/delete" onsubmit={(e) => confirmDelete(room.name, e)}>
									<input type="hidden" name="id" value={room.id} />
									<button
										type="submit"
										class="rounded-md px-2 py-1 text-xs text-danger hover:bg-danger-soft"
									>
										Delete
									</button>
								</form>
							</div>
						</div>
					{/if}
				</li>
			{/each}
		</ul>
	{:else}
		<div class="rounded-lg border border-line bg-surface-raised p-6 text-center">
			<p class="mb-1 text-foreground">No rooms yet.</p>
			<p class="text-sm text-foreground-muted">Create your first room below to organize your devices.</p>
		</div>
	{/if}

	<!-- Create room form -->
	<section class="rounded-lg border border-line bg-surface-raised p-4">
		<h2 class="mb-4 text-md font-medium text-foreground">Create room</h2>

		<form method="POST" action="?/create" class="flex flex-col gap-3">
			<FormField
				name="name"
				type="text"
				required
				label="Room name"
				placeholder="e.g. Living room"
				value={form?.values?.name ?? ''}
			/>

			<label class="flex flex-col gap-1">
				<span class="text-sm">Description (optional)</span>
				<textarea
					name="description"
					class="rounded-md border border-line bg-surface px-3 py-2 text-sm"
					placeholder="Add a description for this room"
					rows="3"
				>{form?.values?.description ?? ''}</textarea>
			</label>

			{#if form?.error && form?.values}
				<p class="text-danger">{form.error}</p>
			{/if}

			<button
				type="submit"
				class="self-start rounded-md bg-accent px-4 py-2 text-surface hover:bg-accent-hover"
			>
				Create room
			</button>
		</form>
	</section>
</div>
