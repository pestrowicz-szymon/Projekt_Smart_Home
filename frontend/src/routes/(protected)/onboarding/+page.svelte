<script lang="ts">
	import { resolve } from '$app/paths';
	import { HomeIcon, UsersIcon } from '$lib/components/icons';
</script>

<svelte:head>
	<title>Welcome</title>
</svelte:head>

<div class="mx-auto max-w-md px-4 py-10">
	<h1 class="mb-2 text-center text-2xl">Welcome</h1>
	<p class="mb-8 text-center text-foreground-muted">How would you like to get started?</p>

	<div class="flex flex-col gap-4">
		<a
			href={resolve('/onboarding/create')}
			class="flex items-start gap-4 rounded-lg border border-line bg-surface-raised p-5 transition-colors hover:border-line-accent"
		>
			<span class="rounded-md bg-accent-soft p-2 text-accent">
				<HomeIcon class="h-6 w-6" />
			</span>
			<span class="flex-1">
				<span class="block text-md font-medium text-foreground">Create a home</span>
				<span class="block text-sm text-foreground-muted">
					Start fresh and invite others to join later.
				</span>
			</span>
		</a>

		<a
			href={resolve('/onboarding/join')}
			class="flex items-start gap-4 rounded-lg border border-line bg-surface-raised p-5 transition-colors hover:border-line-accent"
		>
			<span class="rounded-md bg-secondary-soft p-2 text-secondary">
				<UsersIcon class="h-6 w-6" />
			</span>
			<span class="flex-1">
				<span class="block text-md font-medium text-foreground">Join a home</span>
				<span class="block text-sm text-foreground-muted">
					Connect to a home an owner has invited you to.
				</span>
			</span>
		</a>
	</div>
</div>
