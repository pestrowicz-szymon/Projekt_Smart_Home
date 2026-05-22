<script lang="ts">
	import { resolve } from '$app/paths';
	import { HomeIcon, UsersIcon } from '$lib/components/icons';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	const homes = $derived(data.homes);
	const activeHomeId = $derived(data.activeHomeId);
	const currentUserId = $derived(data.currentUserId);

	function roleFor(home: (typeof homes)[number]) {
		if (currentUserId !== null && home.owner.id === currentUserId) return 'Owner';
		const m = home.members.find((m) => m.user.id === currentUserId);
		return m ? m.role.charAt(0).toUpperCase() + m.role.slice(1) : '';
	}
</script>

<svelte:head><title>Your homes</title></svelte:head>

<div class="mx-auto max-w-md px-4 py-8">
	{#if homes.length === 0}
		<h1 class="mb-2 text-center text-2xl">Welcome</h1>
		<p class="mb-8 text-center text-foreground-muted">
			Get started by creating a home or joining one you've been invited to.
		</p>
	{:else}
		<h1 class="mb-1 text-2xl">Your homes</h1>
		<p class="mb-6 text-foreground-muted">Pick a home or add another.</p>

		<ul class="mb-8 divide-y divide-line overflow-hidden rounded-lg border border-line bg-surface-raised">
			{#each homes as home (home.id)}
				{@const active = home.id === activeHomeId}
				<li>
					<a
						href={resolve(`/h/${home.id}/dashboard`)}
						class="flex items-center gap-3 px-4 py-3 transition-colors hover:bg-surface-sunken {active
							? 'border-l-4 border-accent'
							: ''}"
					>
						<span class="rounded-full bg-accent-soft p-2 text-accent">
							<HomeIcon class="h-5 w-5" />
						</span>
						<span class="min-w-0 flex-1">
							<span class="block truncate text-foreground">{home.name}</span>
							<span class="block truncate text-xs text-foreground-subtle">
								{home.devices_count} device{home.devices_count === 1 ? '' : 's'} ·
								{home.members.length + 1} member{home.members.length === 0 ? '' : 's'}
							</span>
						</span>
						<span class="shrink-0 rounded-pill bg-surface-sunken px-2 py-0.5 text-xs text-foreground-muted">
							{roleFor(home)}
						</span>
					</a>
				</li>
			{/each}
		</ul>
	{/if}

	<div class="flex flex-col gap-3">
		<a
			href={resolve('/h/create')}
			class="flex items-start gap-4 rounded-lg border border-line bg-surface-raised p-4 transition-colors hover:border-line-accent"
		>
			<span class="rounded-md bg-accent-soft p-2 text-accent">
				<HomeIcon class="h-5 w-5" />
			</span>
			<span class="flex-1">
				<span class="block font-medium text-foreground">
					{homes.length === 0 ? 'Create a home' : 'Create another home'}
				</span>
				<span class="block text-sm text-foreground-muted">
					You'll be the owner.
				</span>
			</span>
		</a>

		<a
			href={resolve('/h/join')}
			class="flex items-start gap-4 rounded-lg border border-line bg-surface-raised p-4 transition-colors hover:border-line-accent"
		>
			<span class="rounded-md bg-secondary-soft p-2 text-secondary">
				<UsersIcon class="h-5 w-5" />
			</span>
			<span class="flex-1">
				<span class="block font-medium text-foreground">Join a home</span>
				<span class="block text-sm text-foreground-muted">
					Ask the owner to add you.
				</span>
			</span>
		</a>
	</div>
</div>
