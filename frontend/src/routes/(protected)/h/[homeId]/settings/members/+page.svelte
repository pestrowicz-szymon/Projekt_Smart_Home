<script lang="ts">
	import { invalidateAll } from '$app/navigation';
	import { UserIcon } from '$lib/components/icons';
	import type { PageProps } from './$types';
	import type { HomeRole } from '$lib/types/home';
	import toast from 'svelte-french-toast';

	let { data, form }: PageProps = $props();

	const home = $derived(data.home);
	const canManage = $derived(data.canManage);

	const roleStyles: Record<HomeRole, string> = {
		owner: 'bg-accent-soft text-accent',
		admin: 'bg-secondary-soft text-secondary',
		member: 'bg-muted-soft text-muted',
		viewer: 'bg-surface-sunken text-foreground-muted'
	};
	const roles: HomeRole[] = ['admin', 'member', 'viewer'];
	let lastToastKey: string | null = $state(null);

	function displayName(u: { first_name: string; last_name: string; username: string }) {
		const full = `${u.first_name} ${u.last_name}`.trim();
		return full || u.username;
	}

	$effect(() => {
		if (form?.success) {
			invalidateAll();
		}
		const action = form?.action;
		const error = form?.error;
		const success = form?.success;
		if (!action || (!error && !success)) return;

		const key = `${action}:${success ? '1' : '0'}:${error ?? ''}`;
		if (key === lastToastKey) return;

		if (error) {
			toast.error(String(error));
		} else if (success) {
			if (action === 'remove') toast.success('Member removed.');
			else if (action === 'updateRole') toast.success('Member role updated.');
			else if (action === 'add') toast.success('Member added.');
		}
		lastToastKey = key;
	});
</script>

<svelte:head><title>Members · {home.name}</title></svelte:head>

<div>
	<p class="mb-4 text-sm text-foreground-muted">People with access to this home.</p>

	<section class="mb-6">
		<ul
			class="divide-y divide-line overflow-hidden rounded-md border border-line bg-surface-raised"
		>
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
						<span
							class="mt-1 inline-flex rounded-pill px-2 py-0.5 text-xs {roleStyles[member.role]}"
						>
							{member.role}
						</span>
						<p class="truncate text-xs text-foreground-subtle">{member.user.email}</p>
					</div>
					{#if canManage}
						<form method="POST" action="?/updateRole" class="flex items-center gap-2">
							<input type="hidden" name="member_id" value={member.id} />
							<select name="role" class="text-xs">
								{#each roles as role}
									<option value={role} selected={member.role === role}>{role}</option>
								{/each}
							</select>
							<button
								type="submit"
								class="rounded-md px-2 py-1 text-xs text-accent hover:bg-accent-soft"
							>
								Update
							</button>
						</form>
						<form
							method="POST"
							action="?/remove"
							onsubmit={(e) => {
								if (!confirm('Remove this member? They will lose access to the home.')) {
									e.preventDefault();
								}
							}}
						>
							<input type="hidden" name="member_id" value={member.id} />
							<button
								type="submit"
								class="rounded-md px-2 py-1 text-xs text-danger hover:bg-danger-soft"
							>
								Remove
							</button>
						</form>
					{/if}
				</li>
			{/each}
		</ul>
	</section>
</div>
