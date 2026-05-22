<script lang="ts">
	import { invalidateAll } from '$app/navigation';
	import { UserIcon } from '$lib/components/icons';
	import type { PageProps } from './$types';
	import type { HomeRole } from '$lib/types/home';

	let { data, form }: PageProps = $props();

	const home = $derived(data.home);
	const canManage = $derived(data.canManage);

	const roleStyles: Record<HomeRole, string> = {
		owner: 'bg-accent-soft text-accent',
		admin: 'bg-secondary-soft text-secondary',
		member: 'bg-muted-soft text-muted',
		viewer: 'bg-surface-sunken text-foreground-muted'
	};

	function displayName(u: { first_name: string; last_name: string; username: string }) {
		const full = `${u.first_name} ${u.last_name}`.trim();
		return full || u.username;
	}

	$effect(() => {
		if (form?.success) {
			invalidateAll();
		}
	});
</script>

<svelte:head><title>Members · {home.name}</title></svelte:head>

<div>
	<p class="mb-4 text-sm text-foreground-muted">People with access to this home.</p>

	<section class="mb-6">
		<ul class="divide-y divide-line overflow-hidden rounded-md border border-line bg-surface-raised">
			<li class="flex items-center gap-3 px-4 py-3">
				<span class="rounded-full bg-accent-soft p-2 text-accent">
					<UserIcon class="h-5 w-5" />
				</span>
				<div class="min-w-0 flex-1">
					<p class="truncate text-foreground">{displayName(home.owner)}</p>
					<p class="truncate text-xs text-foreground-subtle">{home.owner.email}</p>
				</div>
				<span class="rounded-pill px-2 py-0.5 text-xs {roleStyles.owner}">Owner</span>
			</li>

			{#each home.members as member (member.id)}
				<li class="flex items-center gap-3 px-4 py-3">
					<span class="rounded-full bg-surface-sunken p-2 text-foreground-muted">
						<UserIcon class="h-5 w-5" />
					</span>
					<div class="min-w-0 flex-1">
						<p class="truncate text-foreground">{displayName(member.user)}</p>
						<p class="truncate text-xs text-foreground-subtle">{member.user.email}</p>
					</div>
					<span class="rounded-pill px-2 py-0.5 text-xs {roleStyles[member.role]}">
						{member.role}
					</span>
				</li>
			{/each}
		</ul>
	</section>

	{#if canManage}
		<section class="rounded-lg border border-line bg-surface-raised p-4">
			<h2 class="mb-1 text-md font-medium text-foreground">Add member</h2>
			<p class="mb-4 text-sm text-foreground-muted">
				Ask the person to share their User ID from their join screen.
			</p>

			<form method="POST" class="flex flex-col gap-3">
				<label class="flex flex-col gap-1">
					<span class="text-sm">User ID</span>
					<input name="user_id" type="number" min="1" required placeholder="e.g. 42" />
				</label>

				<label class="flex flex-col gap-1">
					<span class="text-sm">Role</span>
					<select name="role">
						<option value="member" selected>Member — can view and use</option>
						<option value="admin">Admin — can manage members and devices</option>
						<option value="viewer">Viewer — read-only access</option>
					</select>
				</label>

				<label class="flex items-center gap-2 text-sm">
					<input name="can_manage_devices" type="checkbox" />
					Can manage devices (regardless of role)
				</label>

				{#if form?.error}
					<p class="text-danger">{form.error}</p>
				{/if}
				{#if form?.success}
					<p class="text-success">Member added.</p>
				{/if}

				<button
					type="submit"
					class="self-start rounded-md bg-accent px-4 py-2 text-surface hover:bg-accent-hover"
				>
					Add member
				</button>
			</form>
		</section>
	{:else}
		<p class="rounded-md border border-line bg-surface-raised p-4 text-sm text-foreground-muted">
			Only owners and admins can add members.
		</p>
	{/if}
</div>
