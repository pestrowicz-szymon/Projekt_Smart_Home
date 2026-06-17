<script lang="ts">
	import { enhance } from '$app/forms';
	import type { HomeMembership } from '$lib/types/auth';
	import type { ActionData, PageData } from './$types';

	let { data }: { data: PageData; form: ActionData } = $props();
</script>

<svelte:head>
	<title>Preferences</title>
</svelte:head>

<div class="flex flex-col gap-8">
	<section>
		<h1 class="mb-2 text-2xl font-bold">Preferences</h1>
		<p class="text-foreground-muted">Manage your home management settings.</p>
	</section>

	{#if data.manageableHomes.length > 0}
		<section class="space-y-4">
			<h2 class="px-2 text-sm font-bold uppercase tracking-wider text-foreground-subtle">
				Home Management
			</h2>
			<div
				class="overflow-hidden rounded-xl border border-line bg-surface-raised divide-y divide-line"
			>
				{#each data.manageableHomes as home (home.id)}
					{@const membership = data.user?.home_memberships.find(
						(m: HomeMembership) => m.home.id === home.id
					)}
					{#if membership}
						<div class="flex items-center justify-between p-4">
							<div>
								<p class="font-medium text-foreground">{home.name}</p>
								<p class="text-xs text-foreground-muted">Role: {membership.role}</p>
							</div>
							<form method="POST" action="?/toggleDeviceManagement" use:enhance>
								<input type="hidden" name="membership_id" value={membership.id} />
								<label class="relative inline-flex cursor-pointer items-center">
									<input
										type="checkbox"
										name="can_manage_devices"
										checked={membership.can_manage_devices}
										onchange={(e) => e.currentTarget.form?.requestSubmit()}
										class="peer sr-only"
									/>
									<div
										class="h-6 w-11 rounded-full bg-line-strong after:absolute after:top-[2px] after:left-[2px] after:h-5 after:w-5 after:rounded-full after:border after:border-gray-300 after:bg-white after:transition-all after:content-[''] peer-checked:bg-accent peer-checked:after:translate-x-full peer-checked:after:border-white peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-accent-focus-ring"
									></div>
									<span class="sr-only">Toggle Device Management</span>
								</label>
							</form>
						</div>
					{/if}
				{/each}
			</div>
		</section>
	{/if}
</div>
